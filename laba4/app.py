from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils import executor

import logging
import os


# Получение токена из переменных окружения
bot_token = os.getenv('API_TOKEN')
# Создание бота с токеном, который выдал в БотФазер при регистрации бота
bot = Bot(token=bot_token)
# Инициализация диспетчера команд
dp = Dispatcher(bot, storage=MemoryStorage())

# Форма, которая хранит информацию о пользователе
class Form(StatesGroup):
    currency = State()  # поле, в котором хранится название валюты
    rate = State()  # поле, в котором хранится курс валюты к рублю
    currency2 = State()  # поле, в котором хранится название валюты
    amount = State()

dict = {}

# Задание 1

# Обработка команды /save_currency
@dp.message_handler(commands=['save_currency'])
async def process_start_command(message: Message):
    await message.reply("Введите название валюты.")
    await Form.currency.set()

# Обработка введенного названия валюты
@dp.message_handler(state=Form.currency)
async def process_currency(message: types.Message, state: FSMContext):
    await state.update_data(currency=message.text)
    await message.reply("Введите курс валюты к рублю:")
    await Form.rate.set()

# Обработка введенного курса валюты к рублю
@dp.message_handler(state=Form.rate)
async def process_rate(message: types.Message, state: FSMContext):
    await state.update_data(rate=int(message.text))
    user_data = await state.get_data()

    currency_name = user_data['currency']
    dict[currency_name] = int(message.text)

    await message.reply("Курс валюты " + user_data['currency'] + " к рублю сохранен.")
    await state.finish()
    print(f"Сохраненные валюты: {dict}")


# Задание 2

# Обработка команды /convert
@dp.message_handler(commands=['convert'])
async def process_convert_command(message: Message):
    await message.reply("Введите название валюты, которую хотите конвертировать:")
    await Form.currency2.set()

# Обработка введенного названия валюты
@dp.message_handler(state=Form.currency2)
async def process_currency_convert(message: types.Message, state: FSMContext):
    await state.update_data(currency2=message.text)
    user_data = await state.get_data()

    if message.text not in dict:
        await message.reply("Курс для этой валюты не сохранен. Сохраните курс с помощью команды /save_currency.")
        await state.finish()
    else:
        await message.reply("Введите сумму в " + user_data['currency2'] + ":")
        await Form.amount.set()

# Обработка введенной суммы в конвертируемой валюте
@dp.message_handler(state=Form.amount)
async def process_amount(message: types.Message, state: FSMContext):
    await state.update_data(amount=int(message.text))
    user_data = await state.get_data()

    # Конвертирование суммы в рубли по сохраненному курсу
    result = int(message.text) * dict[user_data['currency2']]

    await message.reply(f"{message.text} {user_data['currency2']} = {result} рублей")
    await state.finish()


# Точка входа в приложение
if __name__ == '__main__':
    # Инициализация системы логирования
    logging.basicConfig(level=logging.INFO)
    # Подключение системы логирования к боту
    dp.middleware.setup(LoggingMiddleware())
    # Запуск обработки сообщений
    executor.start_polling(dp, skip_updates=True)
