# app/schemas/charity_project.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

from app.core.config import MAX_NAME_LENGTH, MIN_NAME_LENGTH


class CharityProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH
    )
    description: Optional[str] = Field(None, min_length=MIN_NAME_LENGTH)
    full_amount: Optional[PositiveInt]

    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectUpdate):
    name: str = Field(
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH
    )
    description: str = Field(min_length=MIN_NAME_LENGTH)
    full_amount: PositiveInt


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
