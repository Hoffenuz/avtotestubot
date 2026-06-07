import time

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

START_COOLDOWN_SEC = 3
_last_start: dict[int, float] = {}


class StartDebounceMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            user = event.from_user
            if user:
                now = time.time()
                last = _last_start.get(user.id, 0)
                if now - last < START_COOLDOWN_SEC:
                    return
                _last_start[user.id] = now
        return await handler(event, data)
