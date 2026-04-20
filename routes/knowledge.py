import uuid
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from api.rag import add_user_document, clear_user_documents, get_user_documents

router = APIRouter()


@router.post("/api/upload-knowledge")
async def upload_knowledge(
    files: list[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
):
    """Recibe archivos .md/.txt y los guarda con rag.add_user_document()."""
    if not session_id:
        session_id = str(uuid.uuid4())

    uploaded = []
    for file in files:
        if not file.filename.endswith((".md", ".txt")):
            continue
        content = await file.read()
        text = content.decode("utf-8")
        add_user_document(session_id, file.filename, text)
        uploaded.append(file.filename)

    return {
        "session_id": session_id,
        "uploaded_files": uploaded,
        "total_documents": len(get_user_documents(session_id)),
    }


@router.delete("/api/clear-knowledge/{session_id}")
async def clear_knowledge(session_id: str):
    """Limpia los documentos de una sesión."""
    clear_user_documents(session_id)
    return {"status": "ok", "session_id": session_id}
