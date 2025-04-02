__all__ = [
    "router",
]

from fastapi import APIRouter

from app.io.rest_api.api.v1.candle import router as router_candle
from app.io.rest_api.api.v1.security import router as router_security

router = APIRouter(prefix="/v1")
router.include_router(router_security)
router.include_router(router_candle)
