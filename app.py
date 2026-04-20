from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import PORT
from api.rag import load_knowledge_files
from routes import campaign, styles, knowledge

app = FastAPI(title="CreativoyeooAgent API", version="1.0.0")

# CORS para n8n y cualquier frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas API
app.include_router(campaign.router)
app.include_router(styles.router)
app.include_router(knowledge.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "CreativoyeooAgent"}


@app.on_event("startup")
async def startup_event():
    load_knowledge_files()


# Servir archivos estáticos (UI web) — debe ir después de las rutas API
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True)
