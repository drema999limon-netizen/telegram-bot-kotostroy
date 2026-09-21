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


# Старт бота (/start)
@bot.message_handler(commands=["start"])
def start(message):
    welcome_text = (
        f"👋 <b>Здравствуйте, {message.from_user.first_name}!</b>\n\n"
        f"Добро пожаловать в сервис поиска работы и исполнителей <b>Kotostroy</b>! 🏗✨\n\n"
        f"Пожалуйста, выберите нужный вариант ниже 👇"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


# 1. Нажата кнопка поиска исполнителя (поддерживает ВСЕ варианты нажатия)
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
    template = (
        "📝 <b>Скопируйте текст ниже, заполните данные и отправьте в ответном сообщении:</b>\n\n"
        "<code>"
        "ЗАЯВКА: НУЖЕН ИСПОЛНИТЕЛЬ\n"
        "1. Город: \n"
        "2. Какой исполнитель нужен: \n"
        "3. Какого числа: \n"
        "4. В какое время: \n"
        "5. На какой срок: \n"
        "6. На какие задачи нужен исполнитель: \n"
        "7. Ваш номер для связи: \n"
        "8. Как к вам обращаться: \n"
        "9. Дополнительная информация: "
        "</code>"
    )
    bot.send_message(
        message.chat.id,
        template,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


# 2. Нажата кнопка поиска работы
@bot.message_handler(
    func=lambda m: m.text
    in [
        "💼 Нужна работа",
        "Нужна работа",
        "💼 Нужна работа / Подработка",
        "Работа",
    ]
)
def worker(message):
    template = (
        "📝 <b>Скопируйте текст ниже, заполните данные и отправьте в ответном сообщении:</b>\n\n"
        "<code>"
        "АНКЕТА: НУЖНА РАБОТА\n"
        "1. Город: \n"
        "2. Какую работу можете выполнить: \n"
        "3. С какого числа можете начать: \n"
        "4. С каким графиком готовы работать: \n"
        "5. Желаемая зарплата: \n"
        "6. Какой опыт: \n"
        "7. Ваш номер телефона для связи: \n"
        "8. Дополнительная информация: "
        "</code>"
    )
    bot.send_message(
        message.chat.id,
        template,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


# 3. Пересылка любого заполненного сообщения/заявки в Канал
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_name = message.from_user.first_name or "Пользователь"
    user_username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "скрыт"
    )

    post_text = (
        f"🔥 <b>НОВАЯ ЗАЯВКА В КАНАЛЕ!</b> 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Отправитель:</b> <a href='tg://user?id={message.from_user.id}'>{user_name}</a> ({user_username})\n"
        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{message.text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📩 <i>Чтобы связаться, нажмите на имя отправителя выше.</i>"
    )

    try:
        # Публикуем в канал
        bot.send_message(
            CHANNEL_ID,
            post_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        # Отвечаем пользователю
        bot.send_message(
            message.chat.id,
            "🚀 <b>Спасибо! Ваша заявка успешно отправлена в канал!</b>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ <b>Ошибка отправки в канал!</b> Убедитесь, что бот является администратором канала @kotostroy_zayvki.\n\n<code>Детали: {e}</code>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
