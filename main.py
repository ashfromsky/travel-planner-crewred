from fastapi import FastAPI
from config import settings
from datetime import datetime

app = FastAPI(
    title='Travel Planner',
    description='Travel Planner Assessment Project',
    docs_url='/',
    redoc_url='/redoc',
)


@app.get("/ping")
async def ping():
    return {"status": "ok", "current_time": datetime.now()}


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