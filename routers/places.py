from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from repositories.place_repo import PlaceRepository
from repositories.project_repo import ProjectRepository
from schemas.place import PlaceCreate, PlaceResponse, PlaceUpdate
from services.place_service import PlaceService

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])


def get_place_service(db: AsyncSession = Depends(get_session)) -> PlaceService:
    return PlaceService(
        place_repo=PlaceRepository(db),
        project_repo=ProjectRepository(db),
    )


@router.post(
    "/",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a place to a project",
)
async def add_place(
    project_id: int,
    data: PlaceCreate,
    service: PlaceService = Depends(get_place_service),
):
    return await service.add_to_project(project_id, data)


@router.get(
    "/",
    response_model=list[PlaceResponse],
    status_code=status.HTTP_200_OK,
    summary="List all places in a project",
)
async def list_places(
    project_id: int,
    service: PlaceService = Depends(get_place_service),
):
    return await service.get_all(project_id)


@router.get(
    "/{place_id}",
    response_model=PlaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single place in a project",
)
async def get_place(
    project_id: int,
    place_id: int,
    service: PlaceService = Depends(get_place_service),
):
    return await service.get_by_id(project_id, place_id)


@router.patch(
    "/{place_id}",
    response_model=PlaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a place in a project",
)
async def update_place(
    project_id: int,
    place_id: int,
    data: PlaceUpdate,
    service: PlaceService = Depends(get_place_service),
):
    return await service.update(project_id, place_id, data)