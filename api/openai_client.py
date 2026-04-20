import json
from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from api.rag import get_full_context

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """Eres CreativoyeooAgent, un experto en publicidad y marketing digital. 
Tu especialidad es crear frases publicitarias impactantes y prompts para generación de imágenes.
Siempre respondes en español y generas contenido creativo, profesional y persuasivo.
Adaptas tu estilo al tipo de empresa y sus ejes temáticos."""


async def generate_ad_content(
    company_name: str,
    company_info: str,
    ejes: str,
    quantity: int,
    user_id: str,
) -> list[dict]:
    """Genera contenido publicitario: frases + prompts de imagen + estilos usando RAG como contexto."""
    context = get_full_context(user_id)

    user_message = f"""Genera exactamente {quantity} piezas publicitarias para la empresa "{company_name}".

Información de la empresa:
{company_info}

Ejes temáticos: {ejes}

CONTEXTO DE REFERENCIA (guías de diseño, copywriting y marca):
{context}

Responde ÚNICAMENTE con un JSON array. Cada elemento debe tener:
- "frase": frase publicitaria impactante en español
- "prompt_imagen": prompt detallado en inglés para generar la imagen (NO incluir texto en la imagen)
- "estilo": uno de [photo, cartoon, 3d, cyberpunk, studio-shot, painting, comic, pixel-art, anime, sketch, digital-art, origami]

Ejemplo de formato:
[
  {{"frase": "Tu frase aquí", "prompt_imagen": "detailed image prompt in English", "estilo": "photo"}}
]

IMPORTANTE: Varía los estilos entre las piezas. Responde SOLO el JSON array, sin texto adicional."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.8,
        max_tokens=4000,
    )

    content = response.choices[0].message.content.strip()

    # Parsear JSON buscando '[' y ']' en la respuesta
    start = content.find("[")
    end = content.rfind("]")
    if start != -1 and end != -1:
        json_str = content[start : end + 1]
        results = json.loads(json_str)
    else:
        results = json.loads(content)

    return results


async def summarize_company_info(company_name: str, search_results: list[dict]) -> str:
    """Resume la información empresarial encontrada en la web."""
    search_text = "\n".join(
        f"- {r.get('title', '')}: {r.get('body', '')}" for r in search_results
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""Resume la siguiente información sobre la empresa "{company_name}" en un párrafo conciso. 
Incluye: qué hace la empresa, sus productos/servicios principales y su propuesta de valor.

Resultados de búsqueda:
{search_text}

Si no hay información relevante, indica que no se encontró información y sugiere que el usuario proporcione más contexto.""",
            },
        ],
        temperature=0.3,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()
