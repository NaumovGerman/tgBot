import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


if not BOT_TOKEN or not OPENWEATHER_API_KEY:
    raise ValueError("Переменные окружения не установлены!")