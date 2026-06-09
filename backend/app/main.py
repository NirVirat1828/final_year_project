from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.endpoints import router
from app.core.ml_engine import OrangeFreshnessPredictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.ml_engine = OrangeFreshnessPredictor()
    except FileNotFoundError:
        app.state.ml_engine = None
    yield


app = FastAPI(
    title="Electronic Tongue Orange Freshness API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
