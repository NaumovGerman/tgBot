import os
import asyncio
import traceback
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update, ErrorEvent
import uvicorn
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
    error = event.exception
    update = event.update

    print("\n" + "=" * 80)
    print("[ERROR] Exception occurred!")
    print(f"Error type: {type(error).__name__}")
    print(f"Error message: {error}")

    if update.message:
        print(f"User ID: {update.message.from_user.id}")
        print(f"Username: {update.message.from_user.username}")
        print(f"Message text: {update.message.text}")

    print("\nFull traceback:")
    traceback.print_exception(type(error), error, error.__traceback__)
    print("=" * 130 + "\n")

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

app = FastAPI()

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

RENDER_EXTERNAL_URL = os.environ["RENDER_EXTERNAL_URL"]
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"


@app.on_event("startup")
async def on_startup():
    print("🚀 Bot starting (webhook mode)")
    await set_commands(bot)
    await bot.set_webhook(
        WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET or None
    )
    print(f"✅ Webhook set: {WEBHOOK_URL}")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
    print("🛑 Bot stopped")

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    if WEBHOOK_SECRET:
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            return {"ok": False}

    update = Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ["PORT"])
    )
