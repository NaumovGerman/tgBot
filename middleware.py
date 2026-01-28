from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Any
from datetime import datetime

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict], Awaitable[Any]],
        event: Message,
        data: dict
    ) -> Any:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id = event.from_user.id
        username = event.from_user.username or "N/A"
        text = event.text or "[no text]"
        
        print(f"[{timestamp}] user_id={user_id} username={username} text={text}")
        
        try:
            return await handler(event, data)
        except Exception as e:
            print(f"[{timestamp}] [HANDLER ERROR] user_id={user_id} error={type(e).__name__}: {e}")
            raise