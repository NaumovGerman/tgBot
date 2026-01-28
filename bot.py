import asyncio
import traceback
from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from config import BOT_TOKEN
from middleware import LoggingMiddleware
from handlers import profile, water, food, workout, progress, help, charts
from utils import set_commands


bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.message.middleware(LoggingMiddleware())

dp.include_router(help.router)
dp.include_router(profile.router)
dp.include_router(water.router)
dp.include_router(food.router)
dp.include_router(workout.router)
dp.include_router(progress.router)
dp.include_router(charts.router)

@dp.error()
async def error_handler(event: ErrorEvent):
    """Global error handler with detailed logging"""
    error = event.exception
    update = event.update
    
    print("\n" + "="*80)
    print(f"[ERROR] Exception occurred!")
    print(f"Error type: {type(error).__name__}")
    print(f"Error message: {error}")
    
    if update.message:
        print(f"User ID: {update.message.from_user.id}")
        print(f"Username: {update.message.from_user.username}")
        print(f"Message text: {update.message.text}")
    
    print("\nFull traceback:")
    traceback.print_exception(type(error), error, error.__traceback__)
    print("="*130 + "\n")
    
    # Send user-friendly message
    if update.message:
        try:
            error_messages = {
                ValueError: "❌ Неверный формат данных. Проверьте введенные значения.",
                KeyError: "❌ Сначала настройте профиль командой /set_profile",
                IndexError: "❌ Неверный формат команды. Используйте /help для справки.",
            }
            
            user_message = error_messages.get(
                type(error), 
                "❌ Произошла непредвиденная ошибка. Попробуйте позже."
            )
            
            await update.message.answer(user_message)
        except Exception as send_error:
            print(f"[ERROR] Failed to send error message: {send_error}")
    
    return True

async def main():
    print('🤖 Бот запущен')
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())