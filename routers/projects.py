from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from repositories.place_repo import PlaceRepository
from repositories.project_repo import ProjectRepository
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from schemas.place import ProjectWithPlacesResponse
from services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)

def get_project_service(db: AsyncSession = Depends(get_session)) -> ProjectService:
    return ProjectService(
        project_repo=ProjectRepository(db),
        place_repo=PlaceRepository(db),
    )


@router.post(
    "/",
    response_model=ProjectWithPlacesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a travel project",
)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    return await service.create(data)


@router.get(
    "/",
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List all travel projects",
)
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    service: ProjectService = Depends(get_project_service),
):
    return await service.get_all(skip=skip, limit=limit)


@router.get(
    "/{project_id}",
    response_model=ProjectWithPlacesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single travel project",
)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    return await service.get_by_id(project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a travel project",
)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    return await service.update(project_id, data)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a travel project",
)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    await service.delete(project_id)