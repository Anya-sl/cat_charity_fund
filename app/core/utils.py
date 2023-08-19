# app/core/utils.py

from datetime import datetime
from typing import List, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def get_active_objects(
    db_obj_in: Union[CharityProject, Donation],
    session: AsyncSession
) -> List[Union[CharityProject, Donation]]:
    db_objs = await session.execute(
        select(
            db_obj_in
        ).where(
            db_obj_in.fully_invested == False  # noqa
        ).order_by(
            db_obj_in.create_date
        )
    )
    return db_objs.scalars().all()


async def close_fully_invested_object(
    obj: Union[CharityProject, Donation],
) -> None:
    obj.fully_invested = True
    obj.close_date = datetime.now()


async def execute_investment(
    obj_in: Union[CharityProject, Donation],
    session: AsyncSession
):
    db_obj = (CharityProject if isinstance(obj_in, Donation) else Donation)
    active_objects = await get_active_objects(db_obj, session)

    if not active_objects:
        return obj_in

    obj_in_lack = obj_in.full_amount - obj_in.invested_amount
    for active_obj in active_objects:
        active_obj_lack = active_obj.full_amount - active_obj.invested_amount
        to_invest = (obj_in_lack if active_obj_lack >= obj_in_lack
                     else active_obj_lack)

        active_obj.invested_amount += to_invest
        obj_in.invested_amount += to_invest
        obj_in_lack -= to_invest

        if active_obj.full_amount == active_obj.invested_amount:
            await close_fully_invested_object(active_obj)
        if obj_in.full_amount == obj_in.invested_amount:
            await close_fully_invested_object(obj_in)
            break

    await session.commit()
    return obj_in
