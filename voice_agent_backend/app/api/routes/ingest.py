from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends
from app.models.schemas import IngestResponse
from app.core.config import settings, get_embed_dim
from app.services.qdrant_service import QdrantWriteError, create_collection, upsert_points
from app.services.ollama_service import generate_embedding
from app.services.qdrant_service import list_collections
from app.core.limiter import limiter
from app.core.auth import get_current_user
from app.models.user import User
import logging
import asyncio
import re
import uuid
import os
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Chunking constants ─────────────────────────────────────────
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP

# ── STOP WORDS for basic cleaning ──────────────────────────────
STOP_WORDS = {
    "the",
    "is",
    "at",
    "which",
    "on",
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "been",
    "being",
    "by",
    "for",
    "from",
    "has",
    "had",
    "have",
}


def sanitize_filename(filename: Optional[str], fallback_ext: str = ".txt") -> str:
    """Return a filesystem/vector-store safe display filename."""
    raw_name = os.path.basename(filename or "")
    safe_name = "".join(c for c in raw_name if c.isalnum() or c in "._-").strip("._")
    if safe_name:
        return safe_name[:180]
    return f"upload_{int(time.time())}{fallback_ext}"


def _qdrant_write_acknowledged(result: Dict[str, Any]) -> bool:
    if not isinstance(result, dict):
        return False
    if result.get("status") in {"ok", "acknowledged", "completed"}:
        return True
    inner = result.get("result")
    if isinstance(inner, dict):
        return inner.get("status") in {"acknowledged", "completed"} or bool(inner.get("operation_id"))
    return False


def is_heading_line(line: str) -> bool:
    """Detect if a line is a heading/section title."""
    trimmed = line.strip()
    if len(trimmed) < 3 or len(trimmed) > 120:
        return False
    upper_count = sum(1 for c in trimmed if c.isupper() and c.isalpha())
    letter_count = sum(1 for c in trimmed if c.isalpha())
    if letter_count > 3 and upper_count / letter_count > 0.6:
        return True
    if re.match(r"^\d+[\.\)]\s+[A-Z]", trimmed):
        return True
    if re.match(
        r"^(chapter|section|part|appendix|schedule|table|note)\s",
        trimmed,
        re.IGNORECASE,
    ):
        return True
    return False


def is_table_line(line: str) -> bool:
    """Detect if a line is part of a table (tabs or multiple wide spaces)."""
    tab_count = line.count("\t")
    if tab_count >= 2:
        return True
    multi_space_gaps = len(re.findall(r"\s{3,}", line))
    if multi_space_gaps >= 2:
        return True
    return False


def chunk_text_simple(text: str) -> List[str]:
    """Split text into chunks respecting sentence/paragraph boundaries."""
    separators = ["\n\n", "\n", ". ", ", ", " "]

    def recursive_split_inner(txt: str, max_len: int, seps: list) -> List[str]:
        if len(txt) <= max_len:
            return [txt]
        if not seps:
            return [txt[i : i + max_len] for i in range(0, len(txt), max_len)]
        sep = seps[0]
        rest = seps[1:]
        pieces = txt.split(sep)
        if len(pieces) <= 1:
            return recursive_split_inner(txt, max_len, rest)
        result = []
        for piece in pieces:
            if len(piece) <= max_len:
                result.append(piece)
            else:
                result.extend(recursive_split_inner(piece, max_len, rest))
        return result

    raw_pieces = recursive_split_inner(text, CHUNK_SIZE, separators)
    merged = []
    current = ""
    for piece in raw_pieces:
        t = piece.strip()
        if not t:
            continue
        if len(current) + len(t) + 1 <= CHUNK_SIZE:
            current += (" " if current else "") + t
        else:
            if current:
                merged.append(current)
            current = t
    if current:
        merged.append(current)

    # Add overlap
    overlapped = []
    for j, chunk in enumerate(merged):
        if j == 0:
            overlapped.append(chunk)
        else:
            tail = merged[j - 1][-CHUNK_OVERLAP:]
            overlapped.append(tail + " " + chunk)

    return [c for c in overlapped if len(c.strip()) > 20]


def chunk_structured_lines(
    lines: List[str], page_num: int, default_section: str = ""
) -> List[Dict[str, Any]]:
    """
    Section-aware chunking with metadata.
    Replicates chunkStructuredLines() from script.js.
    """
    all_chunks = []
    current_section = default_section
    current_subsection = ""
    current_block = ""
    current_type = "paragraph"
    block_start_type = "paragraph"
    chunk_index_in_section = 0

    def flush_block():
        nonlocal current_block, block_start_type, current_type, chunk_index_in_section
        t = current_block.strip()
        if len(t) < 15:
            current_block = ""
            return

        if len(t) > CHUNK_SIZE:
            sub_chunks = chunk_text_simple(t)
            for sc in sub_chunks:
                all_chunks.append(
                    {
                        "text": sc,
                        "page": page_num or 0,
                        "section": current_section,
                        "subsection": current_subsection,
                        "chunk_type": block_start_type,
                        "section_chunk_index": chunk_index_in_section,
                    }
                )
                chunk_index_in_section += 1
        else:
            all_chunks.append(
                {
                    "text": t,
                    "page": page_num or 0,
                    "section": current_section,
                    "subsection": current_subsection,
                    "chunk_type": block_start_type,
                    "section_chunk_index": chunk_index_in_section,
                }
            )
            chunk_index_in_section += 1
        current_block = ""

    for line in lines:
        line = line.replace("\u00a0", " ").rstrip()
        if not line.strip():
            if current_type != "table" and len(current_block) > CHUNK_SIZE * 0.6:
                flush_block()
            continue

        if is_heading_line(line):
            flush_block()
            trimmed_heading = line.strip()
            is_subsection = re.match(r"^\d+\.\d+", trimmed_heading) or (
                len(trimmed_heading) > 40
                and not re.match(r"^[A-Z\s]+$", trimmed_heading)
            )
            if is_subsection:
                current_subsection = trimmed_heading
            else:
                current_section = trimmed_heading
                current_subsection = ""
                chunk_index_in_section = 0
            block_start_type = "heading"
            current_type = "paragraph"
            current_block = line + "\n"
            continue

        line_is_table = is_table_line(line) or "|" in line
        if line_is_table and current_type != "table":
            flush_block()
            block_start_type = "table"
            current_type = "table"
        elif not line_is_table and current_type == "table":
            flush_block()
            block_start_type = "paragraph"
            current_type = "paragraph"

        current_block += line + "\n"

        if len(current_block) > CHUNK_SIZE and current_type != "table":
            flush_block()
            block_start_type = current_type
        if len(current_block) > CHUNK_SIZE * 2:
            flush_block()
            block_start_type = current_type

    flush_block()
    return all_chunks


def extract_text_from_pdf(file_bytes: bytes) -> tuple[List[str], List[Dict]]:
    """
    Extract text from PDF using pypdf.
    Returns (lines_per_page, page_data_list).
    Since pypdf doesn't do table-aware extraction like PDF.js,
    we use a simpler approach: extract text per page and detect tables.
    """
    try:
        from pypdf import PdfReader
        from io import BytesIO
    except ImportError:
        raise HTTPException(status_code=500, detail="pypdf not installed")

    reader = PdfReader(BytesIO(file_bytes))
    pages_data = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        lines = text.split("\n")
        pages_data.append({"pageNum": page_num, "lines": lines, "text": text})

    return pages_data


def extract_text_from_docx(file_bytes: bytes) -> List[Dict]:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        from io import BytesIO
    except ImportError:
        raise HTTPException(status_code=500, detail="python-docx not installed")

    doc = Document(BytesIO(file_bytes))
    lines = []
    for para in doc.paragraphs:
        lines.append(para.text)

    return [{"pageNum": 0, "lines": lines, "text": "\n".join(lines)}]


def extract_text_from_txt(file_bytes: bytes) -> List[Dict]:
    """Extract text from plain TXT or CSV."""
    text = file_bytes.decode("utf-8", errors="ignore")
    lines = text.split("\n")
    return [{"pageNum": 0, "lines": lines, "text": text}]


async def ingest_document(
    file_bytes: bytes, filename: str, collection: str, embed_model: Optional[str] = None
) -> int:
    """
    Full document ingestion pipeline.
    1. Extract text (PDF/DOCX/TXT/CSV)
    2. Chunk with section awareness
    3. Embed each chunk
    4. Upsert to Qdrant
    Returns number of chunks created.
    """
    # Determine file type and extract text
    name_lower = filename.lower()
    if name_lower.endswith(".pdf"):
        pages_data = extract_text_from_pdf(file_bytes)
    elif name_lower.endswith(".docx"):
        pages_data = extract_text_from_docx(file_bytes)
    elif name_lower.endswith(".txt") or name_lower.endswith(".csv"):
        pages_data = extract_text_from_txt(file_bytes)
    else:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {filename}"
        )

    # Check we have content
    total_text = sum(len(p.get("text", "")) for p in pages_data)
    if total_text < 50:
        raise HTTPException(
            status_code=400, detail="No readable text found in document"
        )

    # Chunk document
    all_chunks = []
    for page_data in pages_data:
        chunks = chunk_structured_lines(
            page_data.get("lines", []), page_data.get("pageNum", 0), ""
        )
        all_chunks.extend(chunks)

    if not all_chunks:
        raise HTTPException(status_code=400, detail="Could not create text chunks")

    # Add section context prefix and overlap (replicates script.js lines 3414-3430)
    for k in range(1, len(all_chunks)):
        if (
            all_chunks[k].get("section")
            and all_chunks[k]["section"] not in all_chunks[k]["text"]
        ):
            all_chunks[k]["text"] = (
                f"[Section: {all_chunks[k]['section']}]\n{all_chunks[k]['text']}"
            )
        if (
            all_chunks[k].get("subsection")
            and all_chunks[k]["subsection"] not in all_chunks[k]["text"]
        ):
            all_chunks[k]["text"] = (
                f"[Subsection: {all_chunks[k]['subsection']}]\n{all_chunks[k]['text']}"
            )

        # Add semantic overlap from previous chunk
        prev_tail = all_chunks[k - 1]["text"][-CHUNK_OVERLAP:]
        last_sent_end = prev_tail.rfind(". ")
        if last_sent_end > 0:
            prev_tail = prev_tail[last_sent_end + 2 :]
        if 10 < len(prev_tail) < CHUNK_OVERLAP:
            all_chunks[k]["text"] = "..." + prev_tail + " " + all_chunks[k]["text"]

    # Filter short chunks
    all_chunks = [c for c in all_chunks if len(c["text"].strip()) > 20]

    # Ensure collection exists
    collections = await list_collections()
    if collection not in collections:
        active_embed_model = embed_model or settings.EMBED_MODEL
        vector_size = get_embed_dim(active_embed_model)
        await create_collection(collection, vector_size)

    # Determine embedding model
    active_embed_model = embed_model or settings.EMBED_MODEL

    # --- NITRO 5 OPTIMIZATION: Batched Parallel Embedding ---
    points = []
    batch_size = settings.GPU_BATCH_SIZE 
    
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        try:
            # Parallelize embedding for the batch
            tasks = [generate_embedding(chunk["text"], model=active_embed_model) for chunk in batch]
            embeddings = await asyncio.gather(*tasks)
            
            for j, embedding in enumerate(embeddings):
                chunk = batch[j]
                idx = i + j
                points.append({
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "payload": {
                        "text": chunk["text"],
                        "source": filename,
                        "chunk_index": idx,
                        "page": chunk.get("page", 0),
                        "section": chunk.get("section", ""),
                        "subsection": chunk.get("subsection", ""),
                        "section_chunk_index": chunk.get("section_chunk_index", 0),
                        "chunk_type": chunk.get("chunk_type", "paragraph"),
                        "has_table": chunk.get("chunk_type") == "table" or is_table_line(chunk["text"]),
                    },
                })
        except Exception as e:
            logger.warning(f"Batch embedding failed for chunks {i}-{i+batch_size}: {e}")
            continue

    if not points:
        raise HTTPException(status_code=500, detail="All chunks failed to embed")

    # Upsert to Qdrant
    upsert_result = await upsert_points(collection, points)
    if not _qdrant_write_acknowledged(upsert_result):
        logger.error("Qdrant upsert did not acknowledge the ingest write.")
        raise HTTPException(status_code=502, detail="Vector store write failed")

    return len(points)


@router.post("/ingest", response_model=IngestResponse)
@limiter.limit("5/minute")
async def ingest_endpoint(
    request: Request,
    file: UploadFile = File(...),
    collection: str = Form("agent_knowledge", min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9_-]+$"),
    embed_model: Optional[str] = Form(None),
    _current_user: User = Depends(get_current_user),
):
    """
    Accept multipart file upload, extract text, chunk, embed, upsert to Qdrant.
    Supports PDF, DOCX, TXT, CSV.
    """
    # 1. Validate File Size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {settings.MAX_FILE_SIZE // (1024 * 1024)}MB",
        )
    # 2. Validate Extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt", ".csv"]:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file extension: {ext}"
        )

    # 3. Sanitize and Save
    safe_filename = sanitize_filename(file.filename, ext)

    try:
        chunks_created = await ingest_document(
            file_bytes=file_content,
            filename=safe_filename,
            collection=collection,
            embed_model=embed_model,
        )

        return IngestResponse(
            filename=safe_filename,
            chunks_created=chunks_created,
            collection=collection,
            status="success",
        )
    except HTTPException:
        raise
    except QdrantWriteError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {str(e)}")
