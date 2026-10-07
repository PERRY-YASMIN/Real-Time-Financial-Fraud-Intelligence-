from fastapi import FastAPI

from backend.api.routes import router
from backend.api.websocket import router as websocket_router


app = FastAPI(
    title="Financial Crime Intelligence System",
    version="0.1.0",
)


app.include_router(
    router,
    prefix="/api",
)


app.include_router(
    websocket_router,
)