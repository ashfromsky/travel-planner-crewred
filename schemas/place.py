from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PlaceCreate(BaseModel):
    external_id: int


class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None


class PlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    external_id: int
    title: str
    notes: Optional[str]
    is_visited: bool
    created_at: datetime


class ProjectWithPlacesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    status: str
    created_at: datetime
    places: list[PlaceResponse] = []