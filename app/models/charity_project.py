# app/models/charity_project.py

from sqlalchemy import Column, String, Text

from app.core.db import BaseDonationCharity


class CharityProject(BaseDonationCharity):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
