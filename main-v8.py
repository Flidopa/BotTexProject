import aiogram
import asyncio
import logging
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

logging.basicConfig(level=logging.INFO)

API_TOKEN = 'Скрыто'
OWM_API_KEY = 'Скрыто'

ALLOWED_CITIES = {
    'Москва': 'Moscow',
    'Норильск': 'Norilsk',
    'Красноярск': 'Krasnoyarsk',
    'Калининград': 'Kaliningrad'
}

def get_tourist_advice(city_russian: str) -> str:
    advice = {
        "Москва": ("Не пропустите посещение Красной площади и Кремля. "
                   "Также советуем прогуляться по Арбату и посетить местные музеи.\n\n✈️ Кстати дешёвые билеты можно купить на aviasales.ru"),
        "Норильск": ("Одевайтесь тепло и подготовьтесь к северному климату. "
                    "Рекомендуем экскурсии по добывающим предприятиям и природным достопримечательностям.\n\n✈️ Кстати дешёвые билеты можно купить на aviasales.ru"),
        "Красноярск": ("Насладитесь видами Енисея, попробуйте местную кухню и посетите природу в окрестностях города.\n\n✈️ Кстати дешёвые билеты можно купить на aviasales.ru"),
        "Калининград": ("Изучите архитектурное наследие, посетите местные музеи и насладитесь морским климатом.\n\n✈️ Кстати дешёвые билеты можно купить на aviasales.ru")
    }
    return advice.get(city_russian, "😭 Советы для туристов отсутствуют для данного города.")

async def start_handler(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=city, callback_data=f"city_{city}")]
            for city in ALLOWED_CITIES.keys()
        ]
    )
    await message.reply("Добро пожаловать! Выберите город:", reply_markup=keyboard)

async def process_city(callback: types.CallbackQuery):
    city_russian = callback.data.split('_', 1)[1]
    city_query = ALLOWED_CITIES.get(city_russian)
    if not city_query:
        await callback.answer("Выбранный город не поддерживается.", show_alert=True)
        return

    weather = get_weather(city_query)
    if not weather:
        await callback.answer("Не удалось получить данные о погоде.", show_alert=True)
        return

    # Первое сообщение с описанием самого города.
    city_descriptions = {
        "Москва": "Столица России, известна своим богатым культурным наследием и историческими памятниками.",
        "Норильск": "Известен суровыми климатическими условиями и значимыми горнодобывающими предприятиями.",
        "Красноярск": "Город на Енисе с уникальной природой и промышленным развитием.",
        "Калининград": "Уникальный город с немецким наследием и особенностями морского климата."
    }
    description = city_descriptions.get(city_russian, "Описание города не найдено.")
    await callback.message.answer(f"{city_russian}: {description}")
    
    # Второе сообщение с подробной информацией с задержкой в 2 секунды.
    await asyncio.sleep(2)
    message2 = (
        f"Погода в {city_russian}:\n"
        f"🌡️ Температура: {weather['temp']}°C\n"
        f"☁️ Описание: {weather['description']}\n"
        f"💧 Влажность: {weather['humidity']}%\n"
        f"💨 Скорость ветра: {weather['wind_speed']} м/с"
    )
    await callback.message.answer(message2)
    
    # Ждем 3 секунды и отправляем полезные советы для туристов.
    await asyncio.sleep(3)
    advice = get_tourist_advice(city_russian)
    await callback.message.answer(f" ⭐ Полезные советы для туристов:\n{advice}")
    
    await callback.answer()

def get_weather(city: str) -> dict:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        "temp": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"]
    }

async def main():
    bot = Bot(
        token=API_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.message.register(start_handler, Command("start"))
    dp.callback_query.register(process_city, lambda c: c.data and c.data.startswith("city_"))

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())