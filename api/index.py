import os
from flask import Flask, request
import telebot
from telebot import types

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = (
    os.environ.get("BOT_TOKEN")
    or "8643961661:AAFo8pEOThsPy6YggIGRbkugD3rUKKrVS_E"
)
CHANNEL_ID = os.environ.get("CHANNEL_ID") or "@kotostroy_zayvki"
# ===================================================

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)


# Главное меню
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👷 Нужны исполнители")
    btn2 = types.KeyboardButton("💼 Нужна работа")
    markup.add(btn1, btn2)
    return markup


@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def catch_all(path):
    if request.method == "POST":
        if request.headers.get("content-type") == "application/json":
            json_string = request.get_data().decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return "OK", 200
        return "Forbidden", 403
    return "Bot is running!", 200


# 1. Приветствие по команде /start
@bot.message_handler(commands=["start"])
def start(message):
    first_name = message.from_user.first_name or "пользователь"

    welcome_text = (
        f"👋 Здравствуйте, {first_name} !\n\n"
        f"Добро пожаловать в сервис поиска работы и исполнителей Kotostroy! 🏗✨\n\n"
        f"Пожалуйста, выберите нужный вариант ниже 👇"
    )

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


# 2. Шаблон для Заказчика ("Нужны исполнители")
@bot.message_handler(
    func=lambda m: m.text
    in [
        "👷 Нужны исполнители",
        "Нужны исполнители",
        "👷 Нужно найти исполнителя",
        "Исполнители",
    ]
)
def employer(message):
    instruction = "📝 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик, заполните и отправьте ответным сообщением:</b>\n\n"

    template = (
        "<code>"
        "ЗАЯВКА: НУЖЕН ИСПОЛНИТЕЛЬ\n"
        "1. 📍 Адрес: \n"
        "2. 👷 Какой исполнитель нужен: \n"
        "3. 📅 Какого числа: \n"
        "4. ⏰ В какое время: \n"
        "5. ⏳ На какой срок: \n"
        "6. 🛠 На какие задачи нужен исполнитель: \n"
        "7. 📞 Ваш номер для связи: \n"
        "8. 👤 Как к вам обращаться: \n"
        "9. ℹ️ Дополнительная информация: "
        "</code>"
    )

    bot.send_message(
        message.chat.id,
        instruction + template,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


# 3. Шаблон для Исполнителя ("Нужна работа")
@bot.message_handler(
    func=lambda m: m.text
    in [
        "💼 
