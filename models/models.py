from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

class ProjectStatus(str, Enum):
    active = "active"
    completed = "completed"


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    status: ProjectStatus = Field(default=ProjectStatus.active, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    places: list["ProjectPlace"] = Relationship(back_populates="projects")

class ProjectPlace(SQLModel, table=True):
    __tablename__ = "project_places"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", nullable=False)
    external_id: str = Field(nullable=False)
    title: str = Field(max_length=500)
    notes: Optional[str] = Field(default=None)
    is_visited: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    project: Optional[Project] = Relationship(back_populates="places")
