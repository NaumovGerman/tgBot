import matplotlib
matplotlib.use("Agg")

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from utils import users, require_profile

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

router = Router()


def create_progress_chart(user_data: dict) -> io.BytesIO:
    history = user_data.get("history", {})

    water_history = history.get("water", [])
    calories_history = history.get("calories", [])

    # Подготовка данных
    water_dates = [x[0] for x in water_history]
    water_values = [x[1] for x in water_history]

    calorie_dates = [x[0] for x in calories_history]
    calorie_values = [x[1] for x in calories_history]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle("Ваш прогресс", fontsize=16, fontweight="bold")

    if water_dates:
        ax1.plot(
            water_dates,
            water_values,
            marker="o",
            linewidth=2,
            label="Выпито"
        )
        ax1.axhline(
            y=user_data["water_goal"],
            linestyle="--",
            linewidth=2,
            label="Цель",
            c='red'
        )

    ax1.set_ylabel("Вода (мл)")
    ax1.set_title("Потребление воды")
    ax1.legend()
    ax1.grid(alpha=0.3)

    if calorie_dates:
        ax2.plot(
            calorie_dates,
            calorie_values,
            marker="o",
            linewidth=2,
            label="Баланс калорий"
        )
        ax2.axhline(
            y=user_data["calorie_goal"],
            linestyle="--",
            linewidth=1,
            label="Ноль"
        )

    ax2.set_ylabel("Калории (ккал)")
    ax2.set_xlabel("Время")
    ax2.set_title("🔥 Баланс калорий")
    ax2.legend()
    ax2.grid(alpha=0.3)

    # Форматирование дат
    for ax in (ax1, ax2):
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close()

    return buf


@router.message(Command("show_charts"))
@require_profile
async def show_charts(message: Message):
    try:
        user = users[message.from_user.id]

        if not user["history"]["water"] and not user["history"]["calories"]:
            await message.answer("❗ Пока нет данных для построения графиков")
            return

        await message.answer("📊 Строю графики...")

        chart = create_progress_chart(user)
        photo = BufferedInputFile(chart.read(), filename="progress.png")

        await message.answer_photo(
            photo=photo,
            caption=(
                "📊 <b>Дневной прогресс</b>\n\n"
                f"💧 Вода: {user['logged_water']} / {user['water_goal']} мл\n"
                f"🔥 Потреблено: {user['logged_calories']:.0f} ккал\n"
                f"🏃 Сожжено: {user['burned_calories']} ккал"
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        print(f"[ERROR] show_charts: user={message.from_user.id} error={e}")
        await message.answer("❌ Не удалось построить график")
