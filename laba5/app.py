import asyncio
import logging
import os
import psycopg2
from aiogram import Dispatcher, Bot, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault

# Подключение к базе данных
conn = psycopg2.connect(
    database="rpp5",
    user="admin_rpp5",
    password="123",
    host="127.0.0.1")

cursor = conn.cursor()
router = Router()

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


# Классы для хранения состояний
class Currency(StatesGroup):
    state_currency_name = State()
    state_currency_rate = State()


class Conversion(StatesGroup):
    state_currency_name = State()
    state_amount = State()


# Получаем все данные из таблицы admins
cursor.execute("SELECT * FROM admins")
print(cursor.fetchall())


# Функция для создания меню команд
def get_keyboard(message: Message):
    buttons = [
        KeyboardButton(text="/start"),
        KeyboardButton(text="/get_currencies"),
        KeyboardButton(text="/convert")
    ]
    if is_admin(message.chat.id):
        buttons.insert(1, KeyboardButton(text="/manage_currency"))
    # Создаем клавиатуру с параметрами, используя список кнопок
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[buttons])
    # Добавляем кнопку для админов
    return keyboard


# Проверка является ли пользователь администратором
def is_admin(chat_id):
    cursor.execute("SELECT id FROM admins WHERE id = %s", (str(chat_id),))
    return bool(cursor.fetchone())


# Обработка команды /start
@router.message(Command('start'))
async def process_start_command(message: Message):
    if is_admin(message.chat.id):
        hello = "Приветствую вас, администратор!"
    else:
        hello = "Приветствую вас, пользователь!"
    await message.answer(hello, reply_markup=get_keyboard(message))


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


# Обработчик команды добавления валюты
@router.message(F.text == "Добавить валюту")
async def add_currency_command(message: Message, state: FSMContext):
    if is_admin(message.chat.id):
        await message.answer("Введите название валюты:")
        await state.update_data(action="Добавить валюту")
        await state.set_state(Currency.state_currency_name)
    else:
        await message.answer("Нет доступа к команде")
        return


# Обработчик команды удаления валюты
@router.message(F.text == "Удалить валюту")
async def delete_currency_command(message: Message, state: FSMContext):
    if is_admin(message.chat.id):
        await message.answer("Введите название валюты:")
        await state.update_data(action="Удалить валюту")
        await state.set_state(Currency.state_currency_name)
    else:
        await message.answer("Нет доступа к команде")
        return


# Обработчик команды изменения валюты
@router.message(F.text == "Изменить курс валюты")
async def update_currency_command(message: Message, state: FSMContext):
    if is_admin(message.chat.id):
        await message.answer("Введите название валюты:")
        await state.update_data(action="Изменить курс валюты")
        await state.set_state(Currency.state_currency_name)
    else:
        await message.answer("Нет доступа к команде")
        return


# Получение названия валюты
@router.message(Currency.state_currency_name)
async def get_currency_name(message: Message, state: FSMContext):
    currency_name = message.text.upper()
    data = await state.get_data()
    action = data.get('action')
    await state.update_data(currency_name=currency_name)

    if action == "Добавить валюту":
        with conn.cursor() as cursor:  # Используем контекстный менеджер
            cursor.execute(f"SELECT * FROM currencies WHERE currency_name = '{currency_name}'")
            if cursor.fetchone():
                await message.answer("Данная валюта уже существует!")
                await state.clear()
                return
            await message.answer("Введите курс к рублю:")
            await state.set_state(Currency.state_currency_rate)
    elif action == "Удалить валюту":
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM currencies WHERE currency_name = '{currency_name}'")
            conn.commit()
            await message.answer(f"Валюта: {currency_name} успешно удалена!")
            await state.clear()
    elif action == "Изменить курс валюты":
        await message.answer("Введите курс к рублю:")
        await state.set_state(Currency.state_currency_rate)


# Получение курса валюты (для добавления и изменения)
@router.message(Currency.state_currency_rate)
async def get_currency_rate(message: Message, state: FSMContext):
    try:
        currency_rate = float(message.text)
    except ValueError:
        await message.answer("Неверный формат курса. Введите число.")
        return

    data = await state.get_data()
    action = data.get('action')
    currency_name = data.get('currency_name')

    with conn.cursor() as cursor:
        if action == "Добавить валюту":
            cursor.execute(f"INSERT INTO currencies (currency_name, rate) VALUES ('{currency_name}', {currency_rate});")
            conn.commit()
            await message.answer(f"Валюта: {currency_name} успешно добавлена!")
        elif action == "Изменить курс валюты":
            cursor.execute(f"UPDATE currencies SET rate = {currency_rate} WHERE currency_name = '{currency_name}';")
            conn.commit()
            await message.answer(f"Курс валюты {currency_name} успешно изменен")

    await state.clear()



# Команда /get_currencies (доступна всем пользователям)
@router.message(Command('get_currencies'))
async def get_currencies(message: Message):
    with conn.cursor() as cursor:
        cursor.execute("SELECT currency_name, rate FROM currencies")
        currencies = cursor.fetchall()

        if not currencies:
            await message.answer("Нет сохраненных валют!")
        else:
            report = "Сохраненные валюты:\n"
            for currency in currencies:
                currency_name, rate = currency  # Распаковываем кортеж
                report += f"1 {currency_name} = {rate} РУБЛЕЙ\n"
            await message.answer(report)



# Обработка команды /convert
@router.message(Command('convert'))
async def convert_command(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(Conversion.state_currency_name)

# Получение названия валюты для конвертации
@router.message(Conversion.state_currency_name)
async def get_currency_name_for_conversion(message: Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency_name=currency_name)

    with conn.cursor() as cursor:
        cursor.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
        currency_data = cursor.fetchone()

        if not currency_data:
            await message.answer("Данная валюта отсутствует!")
            await state.clear()
        else:
            await state.update_data(currency_data=currency_data)
            await message.answer("Введите сумму:")
            await state.set_state(Conversion.state_amount)


# Получение суммы и расчет результата
@router.message(Conversion.state_amount)
async def get_amount_and_convert(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Введите число!")
        return

    data = await state.get_data()
    currency_name = data['currency_name']
    rate = data['currency_data'][0]  # Получаем курс из кортежа
    result = amount * float(rate)

    await message.answer(f"{amount} {currency_name} = {result:.2f} РУБЛЕЙ")
    await state.clear()


# Точка входа в приложение
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

cursor.close()
conn.close()
