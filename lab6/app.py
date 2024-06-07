import asyncio
import logging
import os
import requests
from aiogram import Dispatcher, Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault

from admin import is_admin, conn, cursor, router, get_keyboard


# Классы для хранения состояний
class Currency(StatesGroup):
    state_currency_name = State()
    state_currency_rate = State()


class Conversion(StatesGroup):
    state_currency_name = State()
    state_amount = State()


# Обработка команды /start
@router.message(Command('start'))
# выполняется асинхронно и позволяет использовать await внутри функции.
async def process_start_command(message: Message):
    if is_admin(message.chat.id):
        hello = "Приветствую вас, администратор!"
    else:
        hello = "Приветствую вас, пользователь!"
    await message.answer(hello, reply_markup=get_keyboard(message))

# Класс для хранения состояний
class CurrencyManagement(StatesGroup):
    state_action = State()
    state_currency_name = State()
    state_currency_rate = State()


# Обработка команды /manage_currency
@router.message(Command('manage_currency'))
async def manage_currency(message: Message):
    if is_admin(message.chat.id):
        keyboard = types.ReplyKeyboardMarkup(keyboard=[
            [types.KeyboardButton(text="Добавить валюту")],
            [types.KeyboardButton(text="Удалить валюту")],
            [types.KeyboardButton(text="Изменить курс валюты")]
        ])
        await message.answer("Выберите действие:", reply_markup=keyboard)
    else:
        await message.answer("Нет доступа к команде")
        return


class CurrencyInput(StatesGroup):
    state_currency_name = State()
    state_currency_rate = State()


@router.message(F.text == 'Добавить валюту')
async def save_currency_process(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты")
    await state.set_state(CurrencyInput.state_currency_name)


@router.message(CurrencyInput.state_currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите курс валюты к рублю")
    await state.set_state(CurrencyInput.state_currency_rate)


@router.message(CurrencyInput.state_currency_rate)
async def process_currency_rate(message: types.Message, state: FSMContext):
    # преобразованме текста сообщения в число с плавающей запятой
    try:
        currency_rate = float(message.text)
        # если пользователь ввел не число, то ошибка
    except ValueError:
        await message.answer("Неверный формат курса. Введите число.")
        return

    data = await state.get_data()
    currency_name = data.get('currency_name')

    # Отправка данных в микросервис
    # данные сохраняются в переменную response
    response = requests.post(
        'http://127.0.0.1:5001/load',
        # передаем данные о валюте, название, курсе
        json={'currency_name': currency_name, 'currency_rate': currency_rate}
    )
    # проверяем статусный код ответа
    if response.status_code == 200:
        await message.answer(f"Валюта '{currency_name}' успешно добавлена.")
    else:
        await message.answer(f"Ошибка при добавлении валюты: {response.text}")

    # сбросить состояние после успешного добавления валюты или в случае ошибки.
    await state.clear()
    print(currency_name)


class CurrencyDelete(StatesGroup):
    state_currency_name = State()

@router.message(F.text == 'Удалить валюту')
async def delete_currency_process(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты, которую хотите удалить")
    await state.set_state(CurrencyDelete.state_currency_name)


@router.message(CurrencyDelete.state_currency_name)
async def delete_currency(message: types.Message, state: FSMContext):
    currency_name = message.text.upper()  # Приводим к верхнему регистру

    # Отправка данных в микросервис
    response = requests.post(
        'http://127.0.0.1:5001/delete_currency',
        json={'currency_name': currency_name}
    )

    if response.status_code == 200:
        await message.answer(f"Валюта '{currency_name}' успешно удалена.")
    else:
        await message.answer(f"Ошибка при удалении валюты: {response.text}")

    await state.clear()


# Изменение валюты
class CurrencyChange(StatesGroup):
    state_currency_name = State()
    state_currency_rate = State()


@router.message(F.text == 'Изменить курс валюты')
async def save_currency_process(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты, у которой хотите изменить курс.")
    await state.set_state(CurrencyChange.state_currency_name)


@router.message(CurrencyChange.state_currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите новый курс валюты к рублю")
    await state.set_state(CurrencyChange.state_currency_rate)


@router.message(CurrencyChange.state_currency_rate)
async def process_currency_rate(message: types.Message, state: FSMContext):
    try:
        new_rate = float(message.text)
    except ValueError:
        await message.answer("Неверный формат курса. Введите число.")
        return

    data = await state.get_data()
    currency_name = data.get('currency_name')

    # Отправка данных в микросервис
    response = requests.post(
        'http://127.0.0.1:5001/update_currency',
        json={'currency_name': currency_name, 'currency_rate': new_rate}
    )

    if response.status_code == 200:
        await message.answer(f"Курс валюты '{currency_name}' успешно обновлен.")
    else:
        await message.answer(f"Ошибка при обновлении курса: {response.text}")

    await state.clear()
    print(currency_name)



# Команда /get_currencies
@router.message(Command('get_currencies'))
async def get_currencies(message: Message):
    # Запрос к микросервису
    currencies = requests.get('http://127.0.0.1:5002/currencies')
    data = currencies.json()
    currency = data.get('message')
    await message.answer(currency)


# Класс для хранения состояний при конвертации
class CurrencyConversion(StatesGroup):
    state_currency_name = State()
    state_amount = State()

# Конвертация
# Команда /convert (доступна всем)
@router.message(Command('convert'))
async def convert_command(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyConversion.state_currency_name)

# Получение названия валюты для конвертации
@router.message(CurrencyConversion.state_currency_name)
async def get_currency_name_for_conversion(message: Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency_name=currency_name)
    await state.set_state(CurrencyConversion.state_amount)
    await message.answer(f"Введите сумму в {currency_name}:")

# Получение суммы и расчет результата
@router.message(CurrencyConversion.state_amount)
async def get_amount_and_convert(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Введите число!")
        return

    data = await state.get_data()
    currency_name = data.get('currency_name')

    # Отправка данных в микросервис
    response = requests.get('http://127.0.0.1:5002/convert',
                            params={'currency_name': currency_name, 'amount': amount})
    conversion_data = response.json()
    response_message = conversion_data.get('message')
    await message.answer(f"Результат: {response_message}")




ADMIN_ID = ['762606808']


async def main():
    # Получение токена из переменных окружения
    bot_token = os.getenv('API_TOKEN')
    # Создание бота с токеном, который выдал в БотФазер при регистрации бота
    bot = Bot(token=bot_token)
    # команды для пользователей
    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Начать работу"),
            BotCommand(command="/convert", description="Конвертировать валюту"),
            BotCommand(command="/get_currencies", description="Получить список всех валют")
        ],
        scope=BotCommandScopeDefault())
    # команды для админов
    for admin in ADMIN_ID:
        await bot.set_my_commands(
            [
                BotCommand(command="/start", description="Начать работу"),
                BotCommand(command="/convert", description="Конвертировать валюту"),
                BotCommand(command="/manage_currency", description="Добавить валюту"),
                BotCommand(command="/get_currencies", description="Получить список всех валют")
            ],
            scope=BotCommandScopeDefault(id=admin))
    # Инициализация диспетчера команд
    dp = Dispatcher()
    # Включение маршрутизатора `router` в диспетчер.
    # Маршрутизатор используется для определения,
    # какой обработчик должен быть вызван для
    # различных команд и событий.
    dp.include_router(router)
    # Обработка сообщений
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

cursor.close()
conn.close()
