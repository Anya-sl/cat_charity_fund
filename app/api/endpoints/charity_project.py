# app/api/endpoints/charity_project.py

from typing import List

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_full_amount_not_decrease,
    check_name_duplicate,
    check_project_exists,
    check_project_invested,
    check_project_is_active
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.core.utils import execute_investment
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
    response_model_exclude={'user_id'},
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех проектов."""
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров. Создает благотворительный проект."""
    await check_name_duplicate(charity_project.name, session)
    new_charity_project = await charity_project_crud.create(
        charity_project, session)
    await execute_investment(new_charity_project, session)
    await session.refresh(new_charity_project)
    return new_charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров. Удаляет проект. Нельзя удалить проект, в который
    уже были инвестированы средства, его можно только закрыть.
    """
    charity_project = await check_project_exists(project_id, session)
    await check_project_invested(charity_project)
    charity_project = await charity_project_crud.remove(
        charity_project, session)
    return charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров. Закрытый проект нельзя редактировать,
    также нельзя установить требуемую сумму меньше уже вложенной.
    """
    charity_project = await check_project_exists(project_id, session)
    await check_project_is_active(charity_project)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount is not None:
        await check_full_amount_not_decrease(
            full_amount=charity_project.full_amount,
            new_full_amount=obj_in.full_amount)
    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    return charity_project
