from typing import Optional
from datetime import datetime, timedelta

from pydantic import BaseModel, Extra, validator, root_validator, Field

FROM_TIME = (
    datetime.now() + timedelta(minutes=10)
).isoformat(timespec='minutes')
TO_TIME = (
    datetime.now() + timedelta(hours=1)
).isoformat(timespec='minutes')


# базовый класс резерва
class ReservationBase(BaseModel):
    from_reserve: datetime = Field(..., example=FROM_TIME)
    to_reserve: datetime = Field(..., example=TO_TIME)

    class Config:
        extra = Extra.forbid


# схема для получения данных
class ReservationUpdate(ReservationBase):

    @validator('from_reserve')
    def check_from_reserve_later_than_now(
        cls,
        value: datetime
    ):
        if value <= datetime.now():
            raise ValueError(
                'Время начала бронирования'
                ' не может быть меньше текущего'
            )
        return value

    @root_validator(skip_on_failure=True)
    # К названию параметров функции-валидатора нет строгих требований.
    # Первым передается класс, вторым — словарь со значениями всех полей.
    def check_from_reserve_before_to_reserve(
        cls,
        values
    ):
        if values['from_reserve'] >= values['to_reserve']:
            raise ValueError(
                'Время окончания резерва не может быть меньше начала'
            )
        return values


# схема для создания
class ReservationCreate(ReservationUpdate):
    meetingroom_id: int


# схема для возврата из БД
class ReservationDB(ReservationBase):
    id: int
    meetingroom_id: int
    # Добавьте опциональное поле user_id.
    user_id: Optional[int]

    class Config:
        orm_mode = True
