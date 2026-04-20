import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY", "")
PORT = int(os.getenv("PORT", 8000))

AVAILABLE_STYLES = [
    "photo", "cartoon", "3d", "cyberpunk", "studio-shot",
    "painting", "comic", "pixel-art", "anime", "sketch",
    "digital-art", "origami"
]
