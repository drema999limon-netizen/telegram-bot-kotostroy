import os
from flask import Flask, request
import telebot
from telebot import types

# Vercel сам подтянет эти данные из настроек, которые мы укажем позже
BOT_TOKEN = 8643961661:AAFo8pEOThsPy6YggIGRbkugD3rUKKrVS_E
ADMIN_ID = 1254118806

if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)


# Функция для создания меню с кнопками
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Нужны исполнители", "Нужна работа")
    return markup


# 1. Прием сообщений от Telegram (Вебхук)
@app.route("/", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Forbidden", 403


# Страница для проверки работы сервера через браузер
@app.route("/", methods=["GET"])
def index():
    return "Бот работает 24/7 на Vercel!"


# 2. Команда /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Здравствуйте! Выберите нужный вариант ниже:",
        reply_markup=get_main_keyboard(),
    )


# 3. Кнопка "Нужны исполнители"
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


# 4. Кнопка "Нужна работа"
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


# 5. Прием заполненной анкеты/заявки и пересылка вам
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text or ""

    # Проверяем, содержит ли сообщение заголовок заявки
    if "ЗАЯВКА:" in text or "АНКЕТА:" in text:
        user_info = (
            f"📩 <b>НОВОЕ СООБЩЕНИЕ ИЗ БОТА</b>\n"
            f"<b>От кого:</b> @{message.from_user.username or 'без_юзернейма'} "
            f"(Имя: {message.from_user.first_name}, ID: {message.from_user.id})\n"
            f"----------------------------------------\n\n"
        )
        full_text = user_info + text

        try:
            bot.send_message(ADMIN_ID, full_text, parse_mode="HTML")
            bot.send_message(
                message.chat.id,
                "✅ Спасибо! Ваша заявка успешно отправлена. Скоро с вами свяжутся.",
                reply_markup=get_main_keyboard(),
            )
        except Exception as e:
            bot.send_message(
                message.chat.id,
                "❌ Произошла ошибка при отправке заявки администратору.",
                reply_markup=get_main_keyboard(),
            )
    else:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, выберите вариант из меню или отправьте заполненную заявку.",
            reply_markup=get_main_keyboard(),
        )