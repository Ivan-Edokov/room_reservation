from fastapi import APIRouter

from app.api.endpoints import (
    meeting_room_router, reservation_router, user_router, google_api_router
)


main_router = APIRouter()

main_router.include_router(
    meeting_room_router, prefix='/meeting_rooms', tags=['Meeting Rooms']
)

main_router.include_router(
    reservation_router, prefix='/reservations', tags=['Reservations']
)

main_router.include_router(user_router)
# Префиксы и теги роутеров библиотеки FastAPI Users
# описаны в файле app/api/endpoints/user.py,
# так что в файле app/api/routers.py будет только подключение,
# и никаких дополнительных параметров.

main_router.include_router(
    google_api_router, prefix='/google', tags=['Google']
)
