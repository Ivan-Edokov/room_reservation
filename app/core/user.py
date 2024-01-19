from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager, FastAPIUsers, IntegerIDMixin, InvalidPasswordException
)
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate


# 2. Добавьте асинхронный генератор get_user_db.
# Он обеспечивает доступ к БД через SQLAlchemy и в
# дальнейшем будет использоваться в качестве
# зависимости (dependency) для объекта класса UserManager:
async def get_user_db(
        session: AsyncSession = Depends(get_async_session)
):
    yield SQLAlchemyUserDatabase(session, User)


# 3. Добавьте компоненты, необходимые для построения
# аутентификационного бэкенда — транспорт, стратегию
# и собственно сам объект бэкенда.
# В FastAPI Users можно создать и использовать
# одновременно несколько бэкендов, поэтому у каждого из них
# должно быть своё уникальное имя.

# Определяем транспорт: передавать токен будем
# через заголовок HTTP-запроса Authorization: Bearer.
# Указываем URL эндпоинта для получения токена.
bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


# Определяем стратегию: хранение токена в виде JWT.
def get_jwt_strategy() -> JWTStrategy:
    # В специальный класс из настроек приложения
    # передаётся секретное слово, используемое для генерации токена.
    # Вторым аргументом передаём срок действия токена в секундах.
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


# Создаём объект бэкенда аутентификации с выбранными параметрами.
auth_backend = AuthenticationBackend(
    name='jwt', # Произвольное имя бэкенда (должно быть уникальным).
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

"""
4. Добавьте класс UserManager и корутину, возвращающую объект 
этого класса.
- Класс UserManager должен быть унаследован:
от миксина IntegerIDMixin — он обеспечивает возможность 
использования целочисленных id для таблицы пользователей.
- от класса BaseUserManager; в этом классе производятся основные действия: 
аутентификация, регистрация, сброс пароля, верификация и другие.

В листинге есть примеры двух (из семи возможных) методов 
класса UserManager, которые разработчик может переопределять: 
для валидации пароля и для действий после успешной регистрации 
пользователя.

Полный список доступных атрибутов и методов класса BaseUserManager 
можно посмотреть в документации.
"""
class UserManager(IntegerIDMixin, BaseUserManager[User, int]):

    # Здесь можно описать свои условия валидации пароля.
    # При успешной валидации функция ничего не возвращает.
    # При ошибке валидации будет вызван специальный класс ошибки
    # InvalidPasswordException.
    async def validate_password(
            self,
            password: str,
            user: Union[UserCreate, User]
    ) -> None:
        if len(password) < 3:
            raise InvalidPasswordException(
                reason='Password should be at least 3 characters'
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason='Password should not contain e-mail'
            )

        # Пример метода для действий после успешной регистрации пользователя.
        async def on_after_register(
                self, user: User, request: Optional[Request] = None
        ):
            # Вместо print здесь можно было бы настроить отправку письма.
            print(f'Пользователь {user.email} зарегистрирован.')


# Корутина, возвращающая объект класса UserManager.
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


# 5. Создаём объект класса FastAPIUsers — это центральный объект
# библиотеки, связывающий объект класса UserManager
# и бэкенд аутентификации.
# Именно этот объект мы будем использовать при подключении роутеров.
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)


# Это методы класса FastAPIUsers, которые мы будем
# использовать в системе Dependency Injection
# для получения текущего пользователя при выполнении запросов,
# а также для разграничения доступа: некоторые эндпоинты
# будут доступны только суперюзерам.
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
