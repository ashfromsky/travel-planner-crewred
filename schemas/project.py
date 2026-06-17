from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.models import ProjectStatus


class PlaceInProjectCreate(BaseModel):
    external_id: int


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = Field(default=None)
    places: Optional[list[PlaceInProjectCreate]] = Field(default=None, max_length=10)


class ProjectUpdate(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    status: ProjectStatus
    created_at: datetime
