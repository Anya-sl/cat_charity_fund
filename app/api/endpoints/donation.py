# app/api/endpoints/donation.py

from typing import List

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.core.utils import execute_investment
from app.crud import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB


router = APIRouter()


@router.get(
    '/my',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    response_model_exclude={'user_id', 'invested_amount', 'fully_invested',
                            'close_date'},
)
async def get_my_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """Получает список всех бронирований для текущего пользователя."""
    donations = await donation_crud.get_by_user(
        session=session, user=user)
    return donations


@router.get(
    '/',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров. Получает список всех пожертвований."""
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    response_model_exclude={'user_id', 'invested_amount', 'fully_invested',
                            'close_date'},
)
async def create_new_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Сделать пожертвование."""
    new_donation = await donation_crud.create(
        donation, session, user)
    await execute_investment(new_donation, session)
    await session.refresh(new_donation)
    return new_donation
