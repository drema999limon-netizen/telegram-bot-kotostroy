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


def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👔 Нужны исполнители", "🛠 Нужна работа")
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


@bot.message_handler(commands=["start"])
def start(message):
    welcome_text = (
        "👋 <b>Здравствуйте! Добро пожаловать в бота.</b>\n\n"
        "Пожалуйста, выберите нужный вариант в меню ниже 👇"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


@bot.message_handler(func=lambda m: m.text and "Нужны исполнители" in m.text)
def employer(message):
    instruction = "📌 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик.</b>\nЗатем вставьте в поле ввода, заполните и отправьте мне:"
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")
    
    # Шаблон отправляется отдельным сообщением для копирования в 1 клик
    template = (
        "<code>📝 ЗАЯВКА: НУЖЕН ИСПОЛНИТЕЛЬ\n"
        "📍 1. Адрес: \n"
        "👷 2. Какой исполнитель нужен: \n"
        "📅 3. Какого числа: \n"
        "⏰ 4. В какое время: \n"
        "⏳ 5. На какой срок: \n"
        "📋 6. На какие задачи: \n"
        "📞 7. Ваш номер: \n"
        "👤 8. Как обращаться: \n"
        "ℹ️ 9. Доп. информация: </code>"
    )
    bot.send_message(message.chat.id, template, parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and "Нужна работа" in m.text)
def worker(message):
    instruction = "📌 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик.</b>\nЗатем вставьте в поле ввода, заполните и отправьте мне:"
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")
    
    # Шаблон отправляется отдельным сообщением для копирования в 1 клик
    template = (
        "<code>💼 АНКЕТА: НУЖНА РАБОТА\n"
        "📍 1. Адрес: \n"
        "🛠 2. Какую работу можете выполнить: \n"
        "🚀 3. С какого числа: \n"
        "⏱ 4. График работы: \n"
        "💰 5. Желаемая зарплата: \n"
        "🧠 6. Какой опыт: \n"
        "📞 7. Ваш номер: \n"
        "ℹ️ 8. Доп. информация: </code>"
    )
    bot.send_message(message.chat.id, template, parse_mode="HTML")
