from fastapi import APIRouter
from config import AVAILABLE_STYLES

router = APIRouter()


@router.get("/api/styles")
async def get_styles():
    """Retorna la lista de estilos disponibles."""
    return {"styles": AVAILABLE_STYLES}
