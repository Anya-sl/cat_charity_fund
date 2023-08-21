# app/crud/base.py

from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
            self,
            session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
            self,
            obj_in,
            session: AsyncSession,
            user: Optional[User] = None
    ):
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        return db_obj

    async def commit_models(
            self,
            obj_list,
            session: AsyncSession,
    ):
        session.add_all(obj_list)
        await session.commit()

    async def update(
            self,
            db_obj,
            obj_in,
            session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True, exclude_none=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
            self,
            db_obj,
            session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_active_objects(
            self,
            obj_in,
            session: AsyncSession
    ):
        db_objs = await session.execute(
            select(
                obj_in
            ).where(
                obj_in.fully_invested == False  # noqa
            ).order_by(
                obj_in.create_date
            )
        )
        return db_objs.scalars().all()

    async def get_project_id_by_name(
            self,
            obj_in,
            obj_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_obj_id = await session.execute(
            select(obj_in.id).where(
                obj_in.name == obj_name
            )
        )
        return db_obj_id.scalars().first()

    async def get_by_user(
        self,
        obj_in,
        user: User,
        session: AsyncSession
    ):
        user_donations = await session.execute(
            select(obj_in).where(obj_in.user_id == user.id)
        )
        return user_donations.scalars().all()
