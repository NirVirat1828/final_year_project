from __future__ import annotations

from contextlib import asynccontextmanager
import logging
import os
import socket
import sys
from pathlib import Path

# Ensure `python main.py` works when launched from `backend/app`.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI
import uvicorn

from app.api.endpoints import router
from app.core.ml_engine import OrangeFreshnessPredictor


logger = logging.getLogger(__name__)


def _is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex((host, port)) != 0


def _resolve_port() -> int:
    env_port = os.getenv("PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            logger.warning("Invalid PORT value %r; falling back to auto-selection", env_port)

    for candidate_port in (8000, 8001, 8002, 8003):
        if _is_port_available("127.0.0.1", candidate_port):
            return candidate_port

    return 8000


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.ml_engine = OrangeFreshnessPredictor()
        logger.info("ML engine loaded successfully")
    except FileNotFoundError:
        app.state.ml_engine = None
        logger.warning("ML engine artifacts were not found; API will start without the model")
    yield
    logger.info("Backend shutdown complete")


app = FastAPI(
    title="Electronic Tongue Orange Freshness API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


if __name__ == "__main__":
    selected_port = _resolve_port()
    logger.info("Starting backend on http://127.0.0.1:%s", selected_port)
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=selected_port,
        reload=False,
        log_level="info",
    )
