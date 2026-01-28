from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils import users, get_temperature, calculate_water, calculate_calories

router = Router()

class ProfileState(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()

@router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите вес (кг):")
    await state.set_state(ProfileState.weight)

@router.message(ProfileState.weight)
async def weight(message: Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    await message.answer("Введите рост (см):")
    await state.set_state(ProfileState.height)

@router.message(ProfileState.height)
async def height(message: Message, state: FSMContext):
    await state.update_data(height=int(message.text))
    await message.answer("Введите возраст:")
    await state.set_state(ProfileState.age)

@router.message(ProfileState.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer("Сколько минут активности в день?")
    await state.set_state(ProfileState.activity)

@router.message(ProfileState.activity)
async def activity(message: Message, state: FSMContext):
    await state.update_data(activity=int(message.text))
    await message.answer("Введите город:")
    await state.set_state(ProfileState.city)

@router.message(ProfileState.city)
async def city(message: Message, state: FSMContext):
    data = await state.get_data()
    city = message.text

    try:
        temperature = await get_temperature(city)
    except:
        temperature = 20

    water_goal = calculate_water(
        data["weight"], data["activity"], temperature
    )
    calorie_goal = calculate_calories(
        data["weight"], data["height"], data["age"], data["activity"]
    )

    users[message.from_user.id] = {
        **data,
        "city": city,
        "water_goal": water_goal,
        "calorie_goal": calorie_goal,
        "logged_water": 0,
        "logged_calories": 0,
        "burned_calories": 0,
        "history": {
            "water": [],
            "calories": []
        }
    }

    await state.clear()
    await message.answer(
        f"✅ Профиль сохранён\n"
        f"💧 Норма воды: {water_goal} мл\n"
        f"🔥 Норма калорий: {calorie_goal} ккал"
    )
