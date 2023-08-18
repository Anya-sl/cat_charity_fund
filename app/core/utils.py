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

    obj_in_shortage = obj_in.full_amount - obj_in.invested_amount
    for obj in active_objects:
        obj_shortage = obj.full_amount - obj.invested_amount
        if obj_shortage >= obj_in_shortage:
            obj.invested_amount += obj_in_shortage
            obj_in.invested_amount += obj_in_shortage
            await close_fully_invested_object(obj_in)
            break
        else:
            obj.invested_amount += obj_shortage
            obj_in.invested_amount += obj_shortage
            obj_in_shortage -= obj_shortage
            await close_fully_invested_object(obj)
    await session.commit()
    return obj_in
