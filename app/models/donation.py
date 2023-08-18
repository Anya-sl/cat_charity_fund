# app/models/donation.py

from sqlalchemy import Column, ForeignKey, Integer, Text

from app.core.db import BaseDonationCharity


class Donation(BaseDonationCharity):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
