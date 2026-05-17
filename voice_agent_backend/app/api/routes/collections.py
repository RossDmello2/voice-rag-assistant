from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import CollectionCreateRequest, DocumentInfo
from app.services.qdrant_service import (
    list_collections,
    create_collection,
    delete_collection,
    list_documents,
    delete_document_vectors,
)
from app.core.config import settings, get_embed_dim

router = APIRouter()


@router.get("/collections")
async def get_collections():
    """List all Qdrant collections."""
    try:
        collections = await list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collections")
async def create_collection_endpoint(
    req: CollectionCreateRequest,
):
    """Create a new Qdrant collection (idempotent)."""
    try:
        embed_model = req.embed_model or settings.EMBED_MODEL
        vector_size = get_embed_dim(embed_model)
        await create_collection(req.name, vector_size)
        return {"name": req.name, "vector_size": vector_size, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{collection_name}")
async def delete_collection_endpoint(
    collection_name: str,
):
    """Delete a Qdrant collection."""
    try:
        await delete_collection(collection_name)
        return {"name": collection_name, "status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_name}/documents")
async def get_documents(collection_name: str):
    """List all documents in a collection (public — used by chat endpoint)."""
    try:
        docs = await list_documents(collection_name)
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{collection_name}/documents/{filename}")
async def delete_document(
    collection_name: str,
    filename: str,
):
    """Delete all vectors for a specific document."""
    try:
        await delete_document_vectors(collection_name, filename)
        return {
            "filename": filename,
            "collection": collection_name,
            "status": "deleted",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
