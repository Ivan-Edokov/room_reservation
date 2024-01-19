from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

from app.core.db import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    ...


"""
ПРИМЕР РАСШИРЕНИЯ МОДЕЛИ ЮЗЕР
В модель добавляются новые поля, расширяющие её:

# app/models/user.py
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

# Новый импорт.
from sqlalchemy import Column, DateTime, String, Text

from app.core.db import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    first_name = Column(String, nullable=False)
    birthdate = Column(DateTime) 


...и те же поля добавляются в схемы:
# app/schemas/user.py
import datetime
from typing import Optional

from fastapi_users import schemas

class UserRead(schemas.BaseUser[int]):
    first_name: str
    birthdate: Optional[datetime.date]

class UserCreate(schemas.BaseUserCreate):
    first_name: str
    birthdate: Optional[datetime.date]

class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str]
    birthdate: Optional[datetime.date]
"""