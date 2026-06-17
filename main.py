from fastapi import FastAPI

from config import settings
from database import init_db
from routers import projects, places

from datetime import datetime
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

def create_app() -> FastAPI:
    inner_app = FastAPI(
        title='Travel Planner',
        description='Travel Planner Assessment Project',
        docs_url='/',
        redoc_url='/redoc',

        version='1.0.0',
        lifespan=lifespan
    )

    inner_app.include_router(projects.router, prefix="/api/v1")
    inner_app.include_router(places.router, prefix="/api/v1")


    @inner_app.get("/ping")
    async def ping():
        return {"status": "ok", "current_time": datetime.now()}

    return inner_app

app = create_app()

if __name__ == '__main__':
    from granian import Granian
    from granian.constants import Interfaces

    Granian(
        "main:app",
        address=settings.HOST,
        port=settings.PORT,
        interface=Interfaces.ASGI,
        workers=settings.WORKERS
    ).serve()