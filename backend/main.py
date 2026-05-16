"""Roadmap Estudos API - FastAPI Backend."""

from contextlib import asynccontextmanager
from pathlib import Path
import sys
from typing import AsyncGenerator

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))  # noqa: E402

import uvicorn  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from backend.api.routes_fastapi import router as api_router  # noqa: E402
from backend.core.config import (  # noqa: E402
    BASE_DIR as CONFIG_BASE_DIR,
    DATA_DIR,
    LICOES_DIR,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize and cleanup application resources."""
    DATA_DIR.mkdir(exist_ok=True)
    LICOES_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="Roadmap Estudos API",
    description="API para gestão de roadmaps de estudo com IA",
    version="1.0.0",
    lifespan=lifespan,
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


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
