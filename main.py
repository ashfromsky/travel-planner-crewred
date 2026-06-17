from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title='Travel Planner',
    description='Travel Planner Assessment Project',
    docs_url='/',
    redoc_url='/redoc',
)



if __name__ == '__main__':
    from granian import Granian
    Granian(
        "main:app",
        address=
    ).serve()
