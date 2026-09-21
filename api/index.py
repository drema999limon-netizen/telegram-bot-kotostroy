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


# 1. Команда /start
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


# 2. Нажата кнопка поиска исполнителя
@bot.message_handler(
    func=lambda m: m.text
    and ("исполнител" in m.text.lower())
    and not ("ЗАЯВКА:" in m.text)
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


# 3. Нажата кнопка поиска работы
@bot.message_handler(
    func=lambda m: m.text
    and ("работ" in m.text.lower())
    and not ("АНКЕТА:" in m.text)
)
def worker(message):
    instruction = "📝 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик, заполните и отправьте ответным сообщением:</b>\n\n"

    template = (
        "<code>"
        "АНКЕТА: НУЖНА РАБОТА\n"
        "1. 📍 Адрес: \n"
        "2. 🛠 Какую работу можете выполнить: \n"
        "3. 📅 С какого числа можете начать: \n"
        "4. ⏰ С каким графиком готовы работать: \n"
        "5. 💰 Желаемая зарплата: \n"
        "6. 🎓 Какой опыт: \n"
        "7. 📞 Ваш номер телефона для связи: \n"
        "8. ℹ️ Дополнительная информация: "
        "</code>"
    )

    bot.send_message(
        message.chat.id,
        instruction + template,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


# 4. Обработка заполненной заявки и отправка в Канал
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_name = message.from_user.first_name or "Пользователь"
    user_username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "скрыт"
    )

    post_text = (
        f"📢 <b>НОВАЯ ЗАЯВКА В KOTOSTROY</b>\n"
        f"➖➖━━━━━━━━━━━━━━━━➖➖\n\n"
        f"{message.text}\n\n"
        f"➖➖━━━━━━━━━━━━━━━━➖➖\n"
        f"👤 <b>Отправитель:</b> <a href='tg://user?id={message.from_user.id}'>{user_name}</a> ({user_username})\n"
        f"💬 <b>Связаться:</b> нажмите на имя отправителя выше"
    )

    try:
        bot.send_message(
            CHANNEL_ID,
            post_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        bot.send_message(
            message.chat.id,
            "✅ <b>Ваша заявка успешно опубликована в нашем канале!</b>\n\n"
            "Ожидайте откликов, скоро с вами свяжутся. Спасибо!",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ <b>Ошибка отправки в канал!</b>\nУбедитесь, что бот добавлен в администраторы канала @kotostroy_zayvki.\n\n<code>Детали: {e}</code>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
