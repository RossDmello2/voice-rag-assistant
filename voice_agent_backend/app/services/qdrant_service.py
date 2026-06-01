import httpx
from app.core.config import settings
from typing import Optional
from app.services.http_client import get_http_client
import logging

logger = logging.getLogger(__name__)


class QdrantWriteError(RuntimeError):
    """Raised when a Qdrant write/delete request is not acknowledged."""


def _write_acknowledged(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    if data.get("status") in {"ok", "acknowledged", "completed"}:
        return True
    result = data.get("result")
    if result is True:
        return True
    if isinstance(result, dict):
        return result.get("status") in {"acknowledged", "completed"} or bool(result.get("operation_id"))
    return False


def _require_write_ack(action: str, data: dict) -> dict:
    if _write_acknowledged(data):
        return data
    raise QdrantWriteError(f"Qdrant did not acknowledge {action}")


# ── Qdrant REST API helpers ─────────────────────────────────────────


async def _qdrant_get(path: str, timeout: float = 10.0) -> dict:
    url = f"{settings.QDRANT_BASE}{path}"
    try:
        client = await get_http_client()
        resp = await client.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.warning(f"Qdrant connection failed (GET {path}): {str(e)}")
        return {"result": {}}
    except Exception as e:
        logger.error(f"Qdrant error (GET {path}): {str(e)}")
        return {"result": {}}


async def _qdrant_post(path: str, payload: dict, timeout: float = 30.0) -> dict:
    url = f"{settings.QDRANT_BASE}{path}"
    try:
        client = await get_http_client()
        resp = await client.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.warning(f"Qdrant connection failed (POST {path}): {str(e)}")
        return {"result": {}}
    except Exception as e:
        logger.error(f"Qdrant error (POST {path}): {str(e)}")
        return {"result": {}}


async def _qdrant_put(path: str, payload: dict, timeout: float = 30.0) -> dict:
    url = f"{settings.QDRANT_BASE}{path}"
    try:
        client = await get_http_client()
        resp = await client.put(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.warning(f"Qdrant connection failed (PUT {path}): {str(e)}")
        return {"result": {}}
    except Exception as e:
        logger.error(f"Qdrant error (PUT {path}): {str(e)}")
        return {"result": {}}


async def _qdrant_delete(path: str, timeout: float = 10.0) -> dict:
    url = f"{settings.QDRANT_BASE}{path}"
    try:
        client = await get_http_client()
        resp = await client.delete(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.warning(f"Qdrant connection failed (DELETE {path}): {str(e)}")
        return {"result": {}}
    except Exception as e:
        logger.error(f"Qdrant error (DELETE {path}): {str(e)}")
        return {"result": {}}


# ── Collection operations ────────────────────────────────────────────


async def list_collections() -> list[str]:
    """List all Qdrant collection names."""
    data = await _qdrant_get("/collections")
    return [c["name"] for c in data.get("result", {}).get("collections", [])]


async def create_collection(name: str, vector_size: int) -> dict:
    """Create a Qdrant collection (idempotent)."""
    # Check if collection already exists
    try:
        existing = await list_collections()
        if name in existing:
            return {"name": name, "status": "already_exists"}
    except Exception:
        pass

    payload = {
        "vectors": {
            "size": vector_size,
            "distance": "Cosine",
        }
    }
    return _require_write_ack(
        f"collection create for {name}",
        await _qdrant_put(f"/collections/{name}", payload),
    )


async def delete_collection(name: str) -> dict:
    """Delete a Qdrant collection (this also removes all points inside it)."""
    return _require_write_ack(
        f"collection delete for {name}",
        await _qdrant_delete(f"/collections/{name}"),
    )


async def collection_exists(name: str) -> bool:
    """Check if a collection exists."""
    try:
        collections = await list_collections()
        return name in collections
    except Exception:
        return False


# ── Document operations ──────────────────────────────────────────────


async def list_documents(collection: str) -> list[dict]:
    """
    List unique documents in a collection by scanning point payloads.
    Returns list of {filename, chunks} dicts.
    """
    try:
        # Scroll through all points to find unique sources
        all_sources = {}
        offset = None
        while True:
            payload = {
                "limit": 100,
                "with_payload": True,
                "with_vector": False,
            }
            if offset is not None:
                payload["offset"] = offset

            data = await _qdrant_post(
                f"/collections/{collection}/points/scroll", payload
            )
            result = data.get("result", {})
            points = result.get("points", [])

            for point in points:
                p = point.get("payload", {})
                src = p.get("source", "unknown")
                if src not in all_sources:
                    all_sources[src] = 0
                all_sources[src] += 1

            next_offset = result.get("next_page_offset")
            if not next_offset or not points:
                break
            offset = next_offset

        return [
            {"filename": src, "chunks": count}
            for src, count in all_sources.items()
        ]
    except Exception:
        return []


async def delete_document_vectors(collection: str, filename: str) -> dict:
    """Delete all vectors for a specific document by source filename."""
    payload = {
        "filter": {
            "must": [
                {"key": "source", "match": {"value": filename}}
            ]
        }
    }
    return _require_write_ack(
        f"document delete for {filename}",
        await _qdrant_post(f"/collections/{collection}/points/delete", payload),
    )


# ── Point operations ─────────────────────────────────────────────────


async def upsert_points(collection: str, points: list[dict]) -> dict:
    """Upsert points into a Qdrant collection."""
    # Qdrant expects points with id, vector, payload
    payload = {
        "points": [
            {
                "id": p["id"],
                "vector": p["vector"],
                "payload": p.get("payload", {}),
            }
            for p in points
        ]
    }
    return _require_write_ack(
        f"point upsert for {collection}",
        await _qdrant_put(f"/collections/{collection}/points", payload, timeout=120.0),
    )


async def search_vectors(
    collection: str,
    vector: list[float],
    limit: int = 8,
    score_threshold: float = 0.30,
) -> list[dict]:
    """
    Search for similar vectors in a Qdrant collection.
    Returns list of {id, score, payload} dicts.
    """
    payload = {
        "vector": vector,
        "limit": limit,
        "score_threshold": score_threshold,
        "with_payload": True,
    }
    data = await _qdrant_post(
        f"/collections/{collection}/points/search", payload
    )
    results = data.get("result", [])
    return [
        {
            "id": str(r.get("id", "")),
            "score": r.get("score", 0),
            "payload": r.get("payload", {}),
        }
        for r in results
    ]


# ── Health check ─────────────────────────────────────────────────────


async def health_check() -> bool:
    """Check if Qdrant is reachable."""
    try:
        url = f"{settings.QDRANT_BASE}/collections"
        client = await get_http_client()
        resp = await client.get(url, timeout=5.0)
        if resp.status_code == 200:
            return True
        logger.error(f"Qdrant health check failed: HTTP {resp.status_code}")
        return False
    except Exception as e:
        logger.error(f"Qdrant health check failed: {str(e)}")
        return False
