import os
from flask import Flask, request
import telebot
from telebot import types

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = (
    os.environ.get("BOT_TOKEN")
    or "8643961661:AAFo8pEOThsPy6YggIGRbkugD3rUKKrVS_E"
)

# Вставьте сюда юзернейм вашего канала (ОБЯЗАТЕЛЬНО С СИМВОЛОМ @)
# Пример: CHANNEL_ID = "@my_orders_channel"
CHANNEL_ID = os.environ.get("CHANNEL_ID") or "@kotostroy_zayvki"
# ===================================================

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)


def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Нужны исполнители", "Нужна работа")
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
    bot.send_message(
        message.chat.id,
        "Здравствуйте! Выберите нужный вариант ниже:",
        reply_markup=get_main_keyboard(),
    )


@bot.message_handler(func=lambda m: m.text == "Нужны исполнители")
def employer(message):
    template = (
        "<b>Скопируйте текст ниже, заполните данные и отправьте ответным сообщением:</b>\n\n"
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
    bot.send_message(message.chat.id, template, parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text == "Нужна работа")
def worker(message):
    template = (
        "<b>Скопируйте текст ниже, заполните данные и отправьте ответным сообщением:</b>\n\n"
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
    bot.send_message(message.chat.id, template, parse_mode="HTML")


@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text or ""

    if "ЗАЯВКА:" in text or "АНКЕТА:" in text:
        user_info = (
            f"📩 <b>НОВОЕ СООБЩЕНИЕ ИЗ БОТА</b>\n"
            f"<b>От кого:</b> @{message.from_user.username or 'без_юзернейма'} "
            f"(Имя: {message.from_user.first_name}, ID: {message.from_user.id})\n"
            f"----------------------------------------\n\n"
        )
        full_text = user_info + text

        try:
            # Отправляем сообщение в КАНАЛ
            bot.send_message(CHANNEL_ID, full_text, parse_mode="HTML")
            bot.send_message(
                message.chat.id,
                "✅ Спасибо! Ваша заявка успешно отправлена.",
                reply_markup=get_main_keyboard(),
            )
        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"❌ Ошибка отправки в канал. Убедитесь, что бот добавлен в администраторы канала!\nОшибка: {e}",
                reply_markup=get_main_keyboard(),
            )
    else:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, выберите вариант из меню или отправьте заполненную заявку.",
            reply_markup=get_main_keyboard(),
        )
