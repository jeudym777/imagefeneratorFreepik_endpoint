import aiohttp
from config import FREEPIK_API_KEY

FREEPIK_URL = "https://api.freepik.com/v1/ai/text-to-image"


async def call_api(prompt: str, style: str) -> dict:
    """Genera una imagen con Freepik AI text-to-image."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-freepik-api-key": FREEPIK_API_KEY,
    }
    body = {
        "prompt": prompt,
        "styling": {"style": style},
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(FREEPIK_URL, json=body, headers=headers) as resp:
            response = await resp.json()
            return response
