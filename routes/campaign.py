import asyncio
import base64
import csv
import io
import uuid
import zipfile
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

from api import web_search, openai_client, freepik_client
from config import AVAILABLE_STYLES

router = APIRouter()


class CampaignRequest(BaseModel):
    company_name: str
    ejes: str
    quantity: int = Field(ge=1, le=20)
    style: Optional[str] = None
    session_id: Optional[str] = None


@router.post("/api/generate-campaign")
async def generate_campaign(req: CampaignRequest):
    """Ejecuta el flujo completo de generación de campaña y retorna un ZIP."""
    user_id = req.session_id or str(uuid.uuid4())

    # 1. Buscar info de la empresa en DuckDuckGo
    search_results = await web_search.search_company(req.company_name)

    # 2. Resumir info con GPT
    company_info = await openai_client.summarize_company_info(
        req.company_name, search_results
    )

    # 3. Generar frases + prompts + estilos con RAG
    ad_contents = await openai_client.generate_ad_content(
        req.company_name, company_info, req.ejes, req.quantity, user_id
    )

    # Si se especificó un estilo fijo, aplicarlo a todos
    if req.style and req.style in AVAILABLE_STYLES:
        for item in ad_contents:
            item["estilo"] = req.style

    # 4. Generar imágenes con Freepik
    images = []
    for i, item in enumerate(ad_contents):
        response = await freepik_client.call_api(
            item["prompt_imagen"], item["estilo"]
        )
        img_b64 = None
        try:
            img_b64 = response["data"][0]["base64"]
        except (KeyError, IndexError, TypeError):
            pass
        images.append(img_b64)

        # Rate limiting: esperar 1s entre requests (excepto el último)
        if i < len(ad_contents) - 1:
            await asyncio.sleep(1)

    # 5. Crear ZIP con imágenes + CSV
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # CSV
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Número", "Frase Publicitaria", "Prompt de Imagen", "Estilo", "Archivo"])

        for i, item in enumerate(ad_contents):
            num = i + 1
            filename = f"imagen_{num:02d}.png"

            writer.writerow([
                num,
                item["frase"],
                item["prompt_imagen"],
                item["estilo"],
                filename,
            ])

            if images[i]:
                img_bytes = base64.b64decode(images[i])
                zf.writestr(filename, img_bytes)

        zf.writestr("campaña.csv", csv_buffer.getvalue())

    zip_buffer.seek(0)
    safe_name = req.company_name.replace(" ", "_")[:30]
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="campana_{safe_name}.zip"'
        },
    )
