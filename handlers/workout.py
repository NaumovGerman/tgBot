from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils import users, workout_calories, require_profile

router = Router()

@router.message(Command("log_workout"))
@require_profile
async def log_workout(message: Message):
    try:
        parts = message.text.split()
        *workout_parts, minutes_str = parts[1:]
        workout = " ".join(workout_parts)
        try:
            minutes = int(minutes_str)
            if minutes <= 0:
                raise ValueError
        except ValueError:
            await message.answer("❌ Время тренировки должно быть положительным числом")
            return

        burned = workout_calories(workout, minutes)
        water_goal_incriment = (minutes // 30) * 200

        users[message.from_user.id]["burned_calories"] += burned
        users[message.from_user.id]["water_goal"] += water_goal_incriment

        balance = users[message.from_user.id]["logged_calories"] - users[message.from_user.id]["burned_calories"]
        users[message.from_user.id]["history"]["calories"].append(
            (
                message.date,
                balance
            )
        )


        await message.answer(
            f"🏋️ {workout} {minutes} мин\n"
            f"🔥 Сожжено: {burned} ккал\n"
            f"💧 +{water_goal_incriment} мл воды"
        )
    except Exception as e:
        print(f"[ERROR] log_workout: user={message.from_user.id} error={e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
