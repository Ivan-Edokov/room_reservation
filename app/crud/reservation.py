from typing import Optional

from datetime import datetime
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, between, func, or_, select

from app.crud.base import CRUDBase
from app.models import Reservation, User


class CRUDReservation(CRUDBase):

    async def get_reservations_at_the_same_time(
            self,
            # Добавляем звёздочку, чтобы обозначить, что все дальнейшие параметры
            # должны передаваться по ключу. Это позволит располагать 
            # параметры со значением по умолчанию перед параметрами без таких значений.
            *,
            from_reserve: datetime,
            to_reserve: datetime,
            meetingroom_id: int,
            # Добавляем новый опциональный параметр - id объекта бронирования.
            reservation_id: Optional[int] = None,
            session: AsyncSession,
    ) -> list[Reservation]:
        # Выносим уже существующий запрос в отдельное выражение.
        select_stmt = select(Reservation).where(
                Reservation.meetingroom_id == meetingroom_id,
                and_(
                    from_reserve <= Reservation.to_reserve,
                    to_reserve >= Reservation.from_reserve
                )
            )
        # Если передан id бронирования...
        if reservation_id is not None:
            # ... то к выражению нужно добавить новое условие.
            select_stmt = select_stmt.where(
                # id искомых объектов не равны id обновляемого объекта.
                Reservation.id != reservation_id
            )
        # Выполняем запрос.
        reservations = await session.execute(select_stmt)
        reservations = reservations.scalars().all()
        return reservations

    # получить объекты резервации конкретной переговорки
    async def get_future_reservations_for_room(
            self,
            room_id: int,
            session: AsyncSession
    ):
        reservations = await session.execute(
            select(Reservation).where(
                Reservation.meetingroom_id == room_id,
                Reservation.to_reserve > datetime.now()
            )
        )
        reservations = reservations.scalars().all()
        return reservations

    # Получение объектов бронирования определённого пользователя
    async def get_by_user(
            self,
            user: User,
            session: AsyncSession
    ):
        reservations = await session.execute(
            select(Reservation).where(
                Reservation.user_id == user.id
            )
        )
        reservations = reservations.scalars().all()
        return reservations

    # собрать данные о том, сколько раз за указанный
    # период была забронирована каждая переговорка.
    async def get_count_res_at_the_same_time(
            self,
            from_reserve: datetime,
            to_reserve: datetime,
            session: AsyncSession,
    ) -> list[dict[str, int]]:
        reservations = await session.execute(
            # Получаем количество бронирований переговорок за период
            select([Reservation.meetingroom_id,
                    func.count(Reservation.meetingroom_id)]).where(
                Reservation.from_reserve >= from_reserve,
                Reservation.to_reserve <= to_reserve
            ).group_by(Reservation.meetingroom_id)
        )
        reservations = reservations.all()
        return reservations


reservation_crud = CRUDReservation(Reservation)
