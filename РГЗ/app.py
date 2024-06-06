import asyncio
import logging
import os
import requests
import psycopg2
from aiogram import Dispatcher, Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault

# Подключение к базе данных

conn = psycopg2.connect(
        database="rpp_rgz",
        user="admin_rpp_rgz",
        password="123",
        host="127.0.0.1"
    )
cursor = conn.cursor()
router = Router()


# Класс состояния для регистрации
class Registration(StatesGroup):
    waiting_for_login = State()

# Команда /reg
@router.message(Command("reg"))
# Объявление функций cmd_reg
async def cmd_reg(message: Message, state: FSMContext):
    # получаем идентификатор пользователя
    chat_id = str(message.chat.id)
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    if cursor.fetchone():
        await message.answer("Вы уже зарегистрированы!")
        return
    await state.set_state(Registration.waiting_for_login)
    await message.answer("Введите ваш логин:")

# Обработчик состояния ожидания логина
@router.message(Registration.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text
    chat_id = str(message.chat.id)

    # Сохраняем логин и дату регистрации в базу данных
    cursor.execute("INSERT INTO users (name, chat_id) VALUES (%s, %s)",
                   (login, chat_id))
    conn.commit()
    await message.answer(f"Вы успешно зарегистрированы с логином: {login}")
    await state.clear()



# Класс состояния для добавления операции
class AddOperation(StatesGroup):
    waiting_for_operation_type = State()
    waiting_for_amount = State()
    waiting_for_date = State()

# Команда /add_operation
@router.message(Command("add_operation"))
async def cmd_add_operation(message: Message, state: FSMContext):
    chat_id = str(message.chat.id)
    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    if not cursor.fetchone():
        await message.answer("Необходима регистрация. Используйте команду /reg")
        return

    # Предлагаем выбрать тип операции
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="РАСХОД"), KeyboardButton(text="ДОХОД")]
    ], resize_keyboard=True)
    await message.answer("Выберите тип операции:", reply_markup=keyboard)
    await state.set_state(AddOperation.waiting_for_operation_type)

# Обработчик выбора типа операции
@router.message(AddOperation.waiting_for_operation_type)
async def process_operation_type(message: Message, state: FSMContext):
    operation_type = message.text
    await state.update_data(operation_type=operation_type)
    await message.answer("Введите сумму операции в рублях:")
    await state.set_state(AddOperation.waiting_for_amount)

# Обработчик ввода суммы операции
@router.message(AddOperation.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    amount = float(message.text)
    await state.update_data(amount=amount)
    await message.answer("Укажите дату операции в формате YYYY-MM-DD:")
    await state.set_state(AddOperation.waiting_for_date)

# Обработчик ввода даты операции
@router.message(AddOperation.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    user_data = await state.get_data()
    operation_type = user_data['operation_type']
    amount = user_data['amount']
    chat_id = str(message.chat.id)
    date_chat = message.text
    # Сохраняем операцию в базу данных
    cursor.execute("INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
                   (date_chat, amount, chat_id, operation_type))
    conn.commit()
    await message.answer("Операция успешно добавлена!")
    await state.clear()





class ViewOperations(StatesGroup):
    waiting_for_currency = State()

@router.message(Command("operations"))
async def operations(message: Message, state: FSMContext):
    chat_id = str(message.chat.id)
    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    if not cursor.fetchone():
        await message.answer("Необходима регистрация. Используйте команду /reg")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="RUB"), KeyboardButton(text="EUR"), KeyboardButton(text="USD")],
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите одну из доступных валют:", reply_markup=keyboard)
    await state.set_state(ViewOperations.waiting_for_currency)

@router.message(ViewOperations.waiting_for_currency)
async def process_currency(message: Message, state: FSMContext):
    currency = message.text
    chat_id = str(message.chat.id)
    # Fetch operations from the database
    cursor.execute("SELECT * FROM operations WHERE chat_id = %s", (chat_id,))
    all_operations = cursor.fetchall()

    output = ""
    if currency == "RUB":
        for operation in all_operations:
            output += f"Дата: {operation[1]}, Тип: {operation[4]}, Сумма: {operation[2]} RUB\n"
    else:
        try:
            response = requests.get(f"http://195.58.54.159:8000/rate?currency={currency}")
            response.raise_for_status()
            rate = float(response.json()["rate"])

            for operation in all_operations:
                converted_amount = float(operation[2]) / rate
                output += f"Дата: {operation[1]}, Тип: {operation[4]}, Сумма: {converted_amount:.2f} {currency}\n"

        except requests.exceptions.RequestException as e:
            await message.answer(f"Ошибка при получении курса валют: {e}")
            await state.clear()
            return

    await message.answer(output)
    await state.clear()




class DeleteAccount(StatesGroup):
    waiting_for_delete = State()

# Команда /delaccount
@router.message(Command("delaccount"))
# Объявление функций cmd_reg
async def delete_account_start(message: Message, state: FSMContext):
    chat_id = str(message.chat.id)
    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    if not cursor.fetchone():
        await message.answer("Необходима регистрация. Используйте команду /reg")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ДА"), KeyboardButton(text="НЕТ")],
        ],
        resize_keyboard=True
    )
    await message.answer("Вы уверены что хотите удалить аккаунт?", reply_markup=keyboard)
    await state.set_state(DeleteAccount.waiting_for_delete)

# Обработчик состояния ожидания логина
@router.message(DeleteAccount.waiting_for_delete)
async def process_login(message: Message, state: FSMContext):
    report = message.text
    chat_id = str(message.chat.id)

    if report == "ДА":
        cursor.execute(f"DELETE FROM users WHERE chat_id = %s", (chat_id,))
        cursor.execute("DELETE FROM operations WHERE chat_id = %s", (chat_id,))
        conn.commit()
        await message.answer(f"Ваш аккаунт был успешно удален")
    else:
        await message.answer(f"Удаление аккаунта отменено")
    await state.clear()



async def main():
    bot_token = os.getenv('API_TOKEN')
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands([
        BotCommand(command='reg', description='Регистрация'),
        BotCommand(command='add_operation', description='Добавить операцию'),
        BotCommand(command='operations', description='Просмотреть все операции'),
        BotCommand(command='delaccount', description='Удалить аккаунт')
    ], scope=BotCommandScopeDefault())

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

cursor.close()
conn.close()