import aiohttp
from aiogram import Bot
from aiogram.types import BotCommand, Message
from functools import wraps
from config import OPENWEATHER_API_KEY

users: dict[int, dict] = {}

async def set_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="help", description="Справка по командам"),
        BotCommand(command="set_profile", description="Настройка профиля"),
        BotCommand(command="log_water", description="Записать воду"),
        BotCommand(command="log_food", description="Записать еду"),
        BotCommand(command="log_workout", description="Записать тренировку"),
        BotCommand(command="check_progress", description="Показать прогресс"),
        BotCommand(command="show_charts", description="Показать дневной отчет")
    ])

def calculate_water(weight: int, activity: int, temperature: float) -> int:
    water = weight * 30
    water += (activity // 30) * 500
    if temperature > 25:
        water += 750
    return water


def calculate_calories(weight: int, height: int, age: int, activity: int) -> int:
    bmr = 10 * weight + 6.25 * height - 5 * age
    activity_bonus = min(400, (activity // 30) * 200)
    return int(bmr + activity_bonus)


def workout_calories(workout: str, minutes: int) -> int:
    rates = {
        "бег": 10,
        "ходьба": 5,
        "велосипед": 8,
        "плавание": 9,
        "йога": 4,
        "пилатес": 4,
        "силовая тренировка": 7,
        "кроссфит": 11,
        "аэробика": 6,
        "танцы": 6,
        "скакалка": 12,
        "гребля": 9,
        "лыжи": 8,
        "бокс": 10,
        "растяжка": 3,
    }
    return rates.get(workout.lower(), 6) * minutes



async def get_temperature(city: str) -> float:
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["main"]["temp"]


async def get_food_calories(product: str) -> float:
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": product,
        "search_simple": 1,
        "json": 1,
        "page_size": 1,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            return float(data["products"][0]["nutriments"]["energy-kcal_100g"])


def require_profile(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in users:
            await message.answer(
                "⚠️ Сначала настройте профиль командой /set_profile\n"
                "Используйте /help для справки по командам."
            )
            print(f"[WARNING] User {message.from_user.id} tried to use {func.__name__} without profile")
            return
        return await func(message, *args, **kwargs)
    return wrapper


