from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils import users, get_food_calories, require_profile

router = Router()

class FoodState(StatesGroup):
    grams = State()

@router.message(Command("log_food"))
@require_profile
async def log_food(message: Message, state: FSMContext):
    try:
        product = message.text.split(maxsplit=1)[1]
        kcal_100g = await get_food_calories(product)
    except Exception as e:
        print(f"[ERROR] log_food: user={message.from_user.id} error={e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

    await state.update_data(kcal_100g=kcal_100g)
    await message.answer(
        f"{product} — {kcal_100g} ккал / 100 г\nСколько грамм?"
    )
    await state.set_state(FoodState.grams)

@router.message(FoodState.grams)
async def grams(message: Message, state: FSMContext):
    grams = int(message.text)
    data = await state.get_data()

    calories = grams * data["kcal_100g"] / 100
    users[message.from_user.id]["logged_calories"] += calories
    users[message.from_user.id]["history"]["calories"].append(
        (
            message.date,
            users[message.from_user.id]["logged_calories"]
        )
    )

    await state.clear()
    await message.answer(f"🍽 Записано {calories:.1f} ккал")
