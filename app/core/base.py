
"""Импорты класса Base и всех моделей для Alembic."""

from app.core.db import Base # noqa

# Все модели теперь доступны из файла app/models/__init__.py,
# так что для чистоты кода перепишем здесь
# импорты моделей в одну строку:
from app.models import MeetingRoom, Reservation, User # noqa

# from app.models.meeting_room import MeetingRoom # noqa
# from app.models.reservation import Reservation # noqa
