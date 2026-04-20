import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from pydantic import BaseModel
from api.rag import add_user_document, clear_user_documents, get_user_documents

router = APIRouter()

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge")

class KnowledgeUpdate(BaseModel):
    content: str

# Mapeo de tipos a archivos
KNOWLEDGE_FILES = {
    "brand": "brand_info.md",
    "copywriter": "copywriting_guidelines.md",
    "designer": "design_guidelines.md",
}


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


@router.get("/api/knowledge/{knowledge_type}")
async def get_knowledge(knowledge_type: str):
    """Obtiene el contenido de un archivo de conocimiento (brand, copywriter, designer)."""
    if knowledge_type not in KNOWLEDGE_FILES:
        return {"error": "Tipo de conocimiento no válido"}, 400

    filepath = os.path.join(KNOWLEDGE_DIR, KNOWLEDGE_FILES[knowledge_type])
    if not os.path.exists(filepath):
        return {"content": "", "filename": KNOWLEDGE_FILES[knowledge_type]}

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    return {
        "type": knowledge_type,
        "filename": KNOWLEDGE_FILES[knowledge_type],
        "content": content
    }


@router.put("/api/knowledge/{knowledge_type}")
async def update_knowledge(knowledge_type: str, payload: KnowledgeUpdate):
    """Actualiza el contenido de un archivo de conocimiento."""
    if knowledge_type not in KNOWLEDGE_FILES:
        return {"error": "Tipo de conocimiento no válido"}, 400

    filepath = os.path.join(KNOWLEDGE_DIR, KNOWLEDGE_FILES[knowledge_type])
    
    # Crear directorio si no existe
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    
    # Guardar el contenido
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(payload.content)
    
    # Recargar el knowledge base en memoria
    from api.rag import load_knowledge_files
    load_knowledge_files()
    
    return {
        "status": "ok",
        "type": knowledge_type,
        "filename": KNOWLEDGE_FILES[knowledge_type],
        "message": f"Contenido de {knowledge_type} actualizado"
    }
