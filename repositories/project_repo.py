from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.models import ProjectStatus, Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: int) -> Project | None:
        stmt = (
            select(Project)
            .where(getattr(Project, "id") == project_id)
            .options(selectinload(getattr(Project, "places")))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[Project]:
        stmt = (
            select(Project)
            .options(selectinload(getattr(Project, "places")))
            .order_by(getattr(Project, "created_at").desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete(self, project_id: int) -> None:
        project = await self.get_by_id(project_id)
        if project:
            await self.session.delete(project)
            await self.session.commit()

    async def mark_completed(self, project: Project) -> Project:
        project.status = ProjectStatus.completed
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project