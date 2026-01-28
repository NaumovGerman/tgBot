from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils import users, require_profile

router = Router()

@router.message(Command("check_progress"))
@require_profile
async def check_progress(message: Message):
    try:
        u = users[message.from_user.id]

        await message.answer(
            f"📊 Прогресс\n\n"
            f"💧 Вода: {u['logged_water']} / {u['water_goal']} мл\n\n"
            f"🔥 Калории:\n"
            f"- Потреблено: {u['logged_calories']:.1f} ккал\n"
            f"- Сожжено: {u['burned_calories']} ккал\n"
            f"- Баланс: {u['logged_calories'] - u['burned_calories']:.1f} / {u['calorie_goal']} ккал"
        )
    except Exception as e:
        print(f"[ERROR] log_progress: user={message.from_user.id} error={e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
