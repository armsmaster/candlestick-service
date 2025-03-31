from fastapi import APIRouter

from app.io.rest_api.api.v1 import router as router_v1

router = APIRouter(prefix="/api")
router.include_router(router_v1)
