from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from database.database import bot_db


class IsAdmin(BaseFilter):
    async def __call__(self, id: int) -> bool:
        return id in bot_db.admins
