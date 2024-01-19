from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.reservation import (
    ReservationCreate,
    ReservationDB,
    ReservationUpdate
)
from app.models import Reservation, User
from app.core.db import get_async_session
from app.core.user import current_user
from app.api.validators import (
    check_meeting_room_exists,
    check_reservation_intersections,
    check_reservation_before_edit
)
from app.crud.reservation import reservation_crud
from app.core.user import current_superuser


router = APIRouter()


@router.post(
        '/',
        response_model=ReservationDB
)
async def create_reservation(
    reservation: ReservationCreate,
    session: AsyncSession = Depends(get_async_session),
    # Получаем текущего пользователя и сохраняем в переменную user.
    user: User = Depends(current_user),
):
    await check_meeting_room_exists(reservation.meetingroom_id, session)
    await check_reservation_intersections(**reservation.dict(), session=session)
    # Передаём объект пользователя в метод создания объекта бронирования.
    new_reservation = await reservation_crud.create(
        reservation,
        session,
        user
    )
    return new_reservation


@router.get(
    '/',
    response_model=list[ReservationDB],
    # только суперузер ограничение
    dependencies=[Depends(current_superuser)]
)
async def get_all_reservations(
    session: AsyncSession = Depends(get_async_session)
) -> list[Reservation]:
    # Добавляем докстринг для большей информативности.
    """Только для суперюзеров."""

    all_reservations = await reservation_crud.get_multi(session)
    return all_reservations


@router.delete(
    '/{reservation_id}',
    response_model=ReservationDB,
)
async def delete_reservation(
    reservation_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Для суперюзеров или создателей объекта бронирования."""
    reservation = await check_reservation_before_edit(reservation_id, session, user)
    reservation = await reservation_crud.remove(reservation, session)
    return reservation


@router.patch(
    '/{reservation_id}',
    response_model=ReservationDB
)
async def update_reservation(
    reservation_id: int,
    obj_in: ReservationUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Для суперюзеров или создателей объекта бронирования."""
    # Проверяем, что такой объект бронирования вообще существует.
    reservation = await check_reservation_before_edit(reservation_id, session, user)
    # Проверяем, что нет пересечений с другими бронированиями.
    await check_reservation_intersections(
        # Новое время бронирования, распакованное на ключевые аргументы.
        **obj_in.dict(),
        # id обновляемого объекта бронирования,
        reservation_id=reservation_id,
        # id переговорки.
        meetingroom_id=reservation.meetingroom_id,
        session=session
    )
    reservation = await reservation_crud.update(
        db_obj=reservation,
        # На обновление передаем объект класса ReservationUpdate, как и требуется.
        obj_in=obj_in,
        session=session,
    )
    return reservation


# Получение объектов бронирования определённого пользователя
@router.get(
    '/my_reservations',
    response_model=list[ReservationDB],
    # Добавляем множество с полями, которые надо исключить из ответа.
    response_model_exclude={'user_id'},
)
async def get_my_reservations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    # Сразу можно добавить докстринг для большей информативности.
    """Получает список всех бронирований для текущего пользователя."""
    # Вызываем созданный метод.
    all_me_reservations = await reservation_crud.get_by_user(
        user=user,
        session=session
    )
    return all_me_reservations
