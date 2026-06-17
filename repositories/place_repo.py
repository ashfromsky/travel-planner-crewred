from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import ProjectPlace


class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, place: ProjectPlace) -> ProjectPlace:
        self.session.add(place)
        await self.session.flush()
        await self.session.refresh(place)
        return place

    async def get_by_id(self, place_id: int) -> ProjectPlace | None:
        stmt = select(ProjectPlace).where(ProjectPlace.id == place_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: int) -> list[ProjectPlace]:
        stmt = (
            select(ProjectPlace)
            .where(ProjectPlace.project_id == project_id)
            .order_by(ProjectPlace.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_external_id(
        self, project_id: int, external_id: int
    ) -> ProjectPlace | None:
        stmt = select(ProjectPlace).where(
            ProjectPlace.project_id == project_id,
            ProjectPlace.external_id == external_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_project(self, project_id: int) -> int:
        stmt = select(func.count(ProjectPlace.id)).where(ProjectPlace.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def all_visited(self, project_id: int) -> bool:
        places = await self.get_by_project(project_id)
        if not places:
            return False
        return all(p.is_visited for p in places)

    async def has_visited(self, project_id: int) -> bool:
        places = await self.get_by_project(project_id)
        return any(p.is_visited for p in places)

    async def update(self, place: ProjectPlace) -> ProjectPlace:
        self.session.add(place)
        await self.session.commit()
        await self.session.refresh(place)
        return place