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
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 <b>Здравствуйте, {user_name}!</b>\n\n"
        f"Добро пожаловать в сервис поиска работы и исполнителей <b>Kotostroy!</b> 🏗✨\n\n"
        f"Пожалуйста, выберите нужный вариант ниже 👇"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


@bot.message_handler(func=lambda m: m.text in ["👔 Нужны исполнители", "Нужны исполнители"])
def employer(message):
    # ПЕРВОЕ СООБЩЕНИЕ (Инструкция)
    instruction = "📝 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик, заполните и отправьте ответным сообщением:</b>"
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")
    
    # ВТОРОЕ СООБЩЕНИЕ (Шаблон для копирования без цифр)
    template = (
        "<code>💼 ЗАЯВКА: НУЖЕН ИСПОЛНИТЕЛЬ\n"
        "📍 Адрес: \n"
        "👷 Какой исполнитель нужен: \n"
        "📅 Какого числа: \n"
        "⏰ В какое время: \n"
        "⏳ На какой срок: \n"
        "📋 На какие задачи нужен исполнитель: \n"
        "📞 Ваш номер телефона для связи: \n"
        "👤 Как к вам обращаться: \n"
        "ℹ️ Дополнительная информация: </code>"
    )
    bot.send_message(message.chat.id, template, parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text in ["🛠 Нужна работа", "Нужна работа"])
def worker(message):
    # ПЕРВОЕ СООБЩЕНИЕ (Инструкция)
    instruction = "📝 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик, заполните и отправьте ответным сообщением:</b>"
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")
    
    # ВТОРОЕ СООБЩЕНИЕ (Шаблон для копирования без цифр)
    template = (
        "<code>💼 АНКЕТА: НУЖНА РАБОТА\n"
        "📍 Адрес: \n"
        "🛠 Какую работу можете выполнить: \n"
        "📅 С какого числа можете начать: \n"
        "⏰ С каким графиком готовы работать: \n"
        "💰 Желаемая зарплата: \n"
        "🎓 Какой опыт: \n"
        "📞 Ваш номер телефона для связи: \n"
        "ℹ️ Дополнительная информация: </code>"
    )
    bot.send_message(message.chat.id, template, parse_mode="HTML")


@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'voice', 'audio'])
def handle_all_messages(message):
    # Игнорируем нажатия кнопок, чтобы они не летели в канал
    if message.text in ["👔 Нужны исполнители", "Нужны исполнители", "🛠 Нужна работа", "Нужна работа", "/start"]:
        return

    user_info = (
        f"🔔 <b>НОВОЕ СООБЩЕНИЕ ИЗ БОТА</b> 🔔\n\n"
        f"👤 <b>От кого:</b> @{message.from_user.username or 'Скрыт'} ({message.from_user.first_name})\n"
        f"🆔 <b>ID клиента:</b> <code>{message.from_user.id}</code>\n"
        f"👇 <b>Содержимое заявки:</b> 👇"
    )

    try:
        bot.send_message(CHANNEL_ID, user_info, parse_mode="HTML")
        bot.copy_message(CHANNEL_ID, message.chat.id, message.message_id)
        
        bot.send_message(
            message.chat.id,
            "✅ <b>Отлично!</b> Ваша заявка успешно отправлена.\nСкоро мы с вами свяжемся!",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Произошла ошибка. Убедитесь, что бот является администратором канала.",
            reply_markup=get_main_keyboard(),
        )
# 2. Нажата кнопка 
