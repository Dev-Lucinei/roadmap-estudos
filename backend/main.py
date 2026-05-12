import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes_fastapi import router as api_router
from backend.core.config import DATA_DIR, LICOES_DIR, BASE_DIR as CONFIG_BASE_DIR

app = FastAPI(
    title="Roadmap Estudos API",
    description="API para gestão de roadmaps de estudo com IA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

app.mount(
    "/",
    StaticFiles(directory=str(CONFIG_BASE_DIR / "frontend" / "public"), html=True),
    name="static",
)


@app.on_event("startup")
async def startup_event():
    DATA_DIR.mkdir(exist_ok=True)
    LICOES_DIR.mkdir(exist_ok=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
