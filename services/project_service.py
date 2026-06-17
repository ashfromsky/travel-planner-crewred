from fastapi import HTTPException, status

from models.models import Project, ProjectPlace
from repositories.project_repo import ProjectRepository
from repositories.place_repo import PlaceRepository
from schemas.project import ProjectCreate, ProjectUpdate
from services.aic_service import aic_service


class ProjectService:
    def __init__(self, project_repo: ProjectRepository, place_repo: PlaceRepository):
        self.project_repo = project_repo
        self.place_repo = place_repo

    async def create(self, project_data: ProjectCreate) -> Project:
        session = self.project_repo.session
        try:
            project = Project(
                name=project_data.name,
                description=project_data.description,
                start_date=project_data.start_date,
            )
            project = await self.project_repo.create(project)

            if project.id is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Project ID was not generated.",
                )

            if project_data.places:
                if len(project_data.places) > 10:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="A project cannot have more than 10 places.",
                    )

                for place_data in project_data.places:
                    artwork = await aic_service.get_artwork(place_data.external_id)
                    if not artwork:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Artwork with id={place_data.external_id} not found in AIC API.",
                        )
                    title = artwork["title"]

                    place = ProjectPlace(
                        project_id=project.id,
                        external_id=place_data.external_id,
                        title=title,
                    )
                    await self.place_repo.create(place)

            await session.commit()
        except Exception:
            await session.rollback()
            raise

        db_project = await self.project_repo.get_by_id(project.id)
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project created but could not be retrieved.",
            )
        return db_project

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[Project]:
        return await self.project_repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, project_id: int) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )
        return project

    async def update(self, project_id: int, data: ProjectUpdate) -> Project:
        project = await self.get_by_id(project_id)

        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        if data.start_date is not None:
            project.start_date = data.start_date

        return await self.project_repo.update(project)

    async def delete(self, project_id: int) -> None:
        await self.get_by_id(project_id)

        has_visited = await self.place_repo.has_visited(project_id)
        if has_visited:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete a project that has visited places.",
            )

        await self.project_repo.delete(project_id)