from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils import users, require_profile

router = Router()

@router.message(Command("log_water"))
@require_profile
async def log_water(message: Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: /log_water [количество_мл]\nПример: /log_water 250")
            return
        
        amount = int(parts[1])
        users[message.from_user.id]["logged_water"] += amount
        users[message.from_user.id]["history"]["water"].append(
            (
                message.date,
                users[message.from_user.id]["logged_water"]
            )
        )

        remaining = users[message.from_user.id]["water_goal"] - users[message.from_user.id]["logged_water"]
        await message.answer(
            f"💧 Выпито {amount} мл\n"
            f"Осталось {max(0, remaining)} мл"
        )
    except Exception as e:
        print(f"[ERROR] log_water: user={message.from_user.id} error={e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
