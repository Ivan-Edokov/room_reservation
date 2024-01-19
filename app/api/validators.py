from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.meeting_room import meeting_room_crud
from app.crud.reservation import reservation_crud
from app.core.user import current_user
# Так как в Python-пакете app.models модели импортированы в __init__.py,
# импортировать их можно прямо из пакета.
from app.models import MeetingRoom, Reservation, User


async def check_name_duplicate(
        room_name: str,
        session: AsyncSession,
) -> None:
    # Замените вызов функции на вызов метода.
    room_id = await meeting_room_crud.get_room_id_by_name(room_name, session)
    if room_id is not None:
        raise HTTPException(
            status_code=422,
            detail='Переговорка с таким именем уже существует!',
        )


# проверяет есть такая комната или нет
async def check_meeting_room_exists(
        meeting_room_id: int,
        session: AsyncSession,
) -> MeetingRoom:
    # Замените вызов функции на вызов метода.
    meeting_room = await meeting_room_crud.get(meeting_room_id, session)
    if meeting_room is None:
        raise HTTPException(
            status_code=404,
            detail='Переговорка не найдена!'
        )
    return meeting_room


# проверяет при бронировании перегов. не забронирована на это время
async def check_reservation_intersections(**kwargs) -> None:
    reservations = await reservation_crud.get_reservations_at_the_same_time(
        **kwargs,
    )
    if reservations:
        raise HTTPException(
            status_code=422,
            detail=str(reservations)
        )


# проверяет существует ли запрошенный объект бронирования,
async def check_reservation_before_edit(
        reservation_id: int,
        session: AsyncSession,
        user: User,
) -> Reservation:
    reservation = await reservation_crud.get(reservation_id, session)
    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail='Бронь не найдена!'
        )
    if reservation.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='Невозможно редактировать или удалить чужую бронь!'
        )
    return reservation
