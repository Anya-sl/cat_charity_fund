# app/schemas/donation.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationDB(DonationCreate):
    id: int
    create_date: datetime
    user_id: Optional[int]
    invested_amount: Optional[int]
    fully_invested: Optional[bool]
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
