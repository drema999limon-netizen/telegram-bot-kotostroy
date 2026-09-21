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


# Главное меню с красивыми кнопками
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👷 Нужно найти исполнителя")
    btn2 = types.KeyboardButton("💼 Нужна работа / Подработка")
    markup.add(btn1, btn2)
    return markup


# Маршрут для Vercel
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
        f"Пожалуйста, выберите нужный раздел в меню ниже 👇"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


# Кнопка: "Нужно найти исполнителя"
@bot.message_handler(
    func=lambda m: m.text
    in ["👷 Нужно найти исполнителя", "Нужны исполнители"]
)
def employer(message):
    template = (
        "📝 <b>Скопируйте текст ниже, заполните данные и отправьте в ответном сообщении:</b>\n\n"
        "<code>"
        "✨ ЗАЯВКА: ИЩУ ИСПОЛНИТЕЛЯ ✨\n\n"
        "🏙 1. Город: \n"
        "👨‍🏭 2. Какой исполнитель нужен: \n"
        "📅 3. Какого числа: \n"
        "⏰ 4. В какое время: \n"
        "⏳ 5. На какой срок: \n"
        "🎯 6. Задачи: \n"
        "📞 7. Ваш номер для связи: \n"
        "👤 8. Как к вам обращаться: \n"
        "ℹ️ 9. Дополнительная информация: "
        "</code>"
    )
    bot.send_message(message.chat.id, template, parse_mode="HTML")


# Кнопка: "Нужна работа / Подработка"
@bot.message_handler(
    func=lambda m: m.text in ["💼 Нужна работа / Подработка", "Нужна работа"]
)
def worker(message):
    template = (
        "📝 <b>Скопируйте текст ниже, заполните данные и отправьте в ответном сообщении:</b>\n\n"
        "<code>"
        "✨ АНКЕТА: ИЩУ РАБОТУ ✨\n\n"
        "🏙 1. Город: \n"
        "🛠 2. Какую работу можете выполнить: \n"
        "📅 3. С какого числа можете начать: \n"
        "⏰ 4. График работы: \n"
        "💰 5. Желаемая зарплата: \n"
        "🎓 6. Ваш опыт работы: \n"
        "📞 7. Телефон для связи: \n"
        "ℹ️ 8. Дополнительная информация: "
        "</code>"
    )
    bot.send_message(message.chat.id, template, parse_mode="HTML")


# Пересылка ЛЮБОГО сообщения от пользователя прямо в Канал
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    # Оформляем красивую шапку для сообщения в канале
    user_name = message.from_user.first_name or "Пользователь"
    user_username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "скрыт"
    )

    post_text = (
        f"🔥 <b>НОВАЯ ЗАЯВКА / СООБЩЕНИЕ!</b> 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Отправитель:</b> <a href='tg://user?id={message.from_user.id}'>{user_name}</a> ({user_username})\n"
        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{message.text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📩 <i>Чтобы связаться, нажмите на имя отправителя выше или напишите ему в ЛС.</i>"
    )

    try:
        # Отправляем сообщение в канал
        bot.send_message(
            CHANNEL_ID,
            post_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        # Отвечаем пользователю в боте
        bot.send_message(
            message.chat.id,
            "🚀 <b>Отлично! Ваша заявка мгновенно опубликована в нашем канале!</b>\n\n"
            "Скоро с вами свяжутся. Спасибо!",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ <b>Ошибка публикации в канал!</b>\nУбедитесь, что бот является администратором канала @kotostroy_zayvki.\n\n<code>Детали: {e}</code>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
