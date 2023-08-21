# app/core/utils.py

from datetime import datetime
from typing import List, Union


from app.models import CharityProject, Donation


async def execute_investment(
    target: Union[CharityProject, Donation],
    sources: List[Union[CharityProject, Donation]]
    ) -> List[Union[CharityProject, Donation]]:
    invested_list = []
    if not target.invested_amount:
        target.invested_amount = 0
    for source in sources:
        to_invest = min(target.full_amount - target.invested_amount,
                        source.full_amount - source.invested_amount)
        for obj in (target, source):
            obj.invested_amount += to_invest
            if obj.full_amount == obj.invested_amount:
                obj.close_date = datetime.now()
                obj.fully_invested = True
            invested_list.append(obj)
    return invested_list
