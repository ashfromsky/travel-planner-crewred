from fastapi import HTTPException, status

from models.models import ProjectPlace
from repositories.place_repo import PlaceRepository
from repositories.project_repo import ProjectRepository
from schemas.place import PlaceCreate, PlaceUpdate
from services.aic_service import aic_service


class PlaceService:
    def __init__(self, place_repo: PlaceRepository, project_repo: ProjectRepository):
        self.place_repo = place_repo
        self.project_repo = project_repo

    async def add_to_project(self, project_id: int, data: PlaceCreate) -> ProjectPlace:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        count = await self.place_repo.count_by_project(project_id)
        if count >= 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Project already has the maximum of 10 places.",
            )

        existing = await self.place_repo.get_by_external_id(project_id, data.external_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Place with external_id={data.external_id} already exists in this project.",
            )

        artwork = await aic_service.get_artwork(data.external_id)
        if not artwork:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artwork with id={data.external_id} not found in AIC API.",
            )
        title = artwork["title"]

        place = ProjectPlace(
            project_id=project_id,
            external_id=data.external_id,
            title=title,
        )
        return await self.place_repo.create(place)

    async def get_all(self, project_id: int) -> list[ProjectPlace]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )
        return await self.place_repo.get_by_project(project_id)

    async def get_by_id(self, project_id: int, place_id: int) -> ProjectPlace:
        place = await self.place_repo.get_by_id(place_id)
        if not place or place.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Place with id={place_id} not found in project {project_id}.",
            )
        return place

    async def update(self, project_id: int, place_id: int, data: PlaceUpdate) -> ProjectPlace:
        place = await self.get_by_id(project_id, place_id)

        if data.notes is not None:
            place.notes = data.notes

        if data.is_visited is not None:
            place.is_visited = data.is_visited

        place = await self.place_repo.update(place)

        if data.is_visited:
            all_done = await self.place_repo.all_visited(project_id)
            if all_done:
                project = await self.project_repo.get_by_id(project_id)
                if not project:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Project with id={project_id} not found.",
                    )
                await self.project_repo.mark_completed(project)

        return place