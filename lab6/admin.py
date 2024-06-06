import psycopg2
from aiogram import Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Подключение к базе данных
conn = psycopg2.connect(
        database="rpp6",
        user="admin_rpp6",
        password="123",
        host="127.0.0.1"
    )
cursor = conn.cursor()
router = Router()
# получаем все данные из таблицы admins
cursor.execute("SELECT * FROM admins")
print(cursor.fetchall())

# Проверка является ли пользователь админом
def is_admin(chat_id):
    cursor.execute("SELECT id FROM admins WHERE id = %s", (chat_id,))
    return bool(cursor.fetchone())

# Функция для создания меню команд
def get_keyboard(is_admin):
    buttons = [
        KeyboardButton(text="/start"),
        KeyboardButton(text="/get_currencies"),
        KeyboardButton(text="/convert")
    ]
    if is_admin:
        buttons.insert(1, KeyboardButton(text="/manage_currency"))
    # Создаем клавиатуру с параметрами, используя список кнопок
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[buttons])
    # Добавляем кнопку для админов
    return keyboard



async def currency_exists(currency_name):
    conn = psycopg2.connect(
        database="rpp6",
        user="admin_rpp6",
        password="123",
        host="127.0.0.1"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    currency_name = cur.fetchone()
    conn.close()
    return True if currency_name else False