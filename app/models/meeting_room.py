from sqlalchemy import Column, String, Text
# импорт функции для связи между моделями
from sqlalchemy.orm import relationship

from app.core.db import Base


class MeetingRoom(Base):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    # Установите связь между моделями через функцию relationship.
    reservations = relationship('Reservation', cascade='delete')
