import os
import glob

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge")
MAX_CONTEXT_CHARS = 24000

_knowledge_base: str = ""
_user_docs: dict[str, dict[str, str]] = {}


def load_knowledge_files() -> str:
    """Carga todos los .md y .txt de la carpeta knowledge/."""
    global _knowledge_base
    contents = []
    patterns = [os.path.join(KNOWLEDGE_DIR, "*.md"), os.path.join(KNOWLEDGE_DIR, "*.txt")]
    for pattern in patterns:
        for filepath in sorted(glob.glob(pattern)):
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            contents.append(f"=== {filename} ===\n{text}")
    _knowledge_base = "\n\n".join(contents)
    return _knowledge_base


def add_user_document(user_id: str, filename: str, content: str) -> None:
    """Guarda un documento subido por el usuario en memoria."""
    if user_id not in _user_docs:
        _user_docs[user_id] = {}
    _user_docs[user_id][filename] = content


def get_user_documents(user_id: str) -> dict[str, str]:
    """Obtiene los documentos subidos por un usuario."""
    return _user_docs.get(user_id, {})


def clear_user_documents(user_id: str) -> None:
    """Limpia los documentos de una sesión de usuario."""
    if user_id in _user_docs:
        del _user_docs[user_id]


def _truncate(text: str, max_chars: int) -> str:
    """Corta texto y agrega aviso de truncamiento."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... contenido truncado...]"


def get_full_context(user_id: str) -> str:
    """Combina knowledge base + docs del usuario, trunca a MAX_CONTEXT_CHARS."""
    global _knowledge_base
    if not _knowledge_base:
        load_knowledge_files()

    parts = [_knowledge_base]

    user_documents = get_user_documents(user_id)
    if user_documents:
        user_section = "\n\n=== DOCUMENTOS DEL USUARIO ===\n"
        for fname, content in user_documents.items():
            user_section += f"\n--- {fname} ---\n{content}\n"
        parts.append(user_section)

    full_context = "\n\n".join(parts)
    return _truncate(full_context, MAX_CONTEXT_CHARS)
