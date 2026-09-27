import os
from flask import Flask, request
import telebot
from telebot import types

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "ВСТАВЬТЕ_СЮДА_ВАШ_ТОКЕН"
CHANNEL_ID = os.environ.get("CHANNEL_ID") or "@kotostroy_zayvki"
# ===================================================

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)


# ==================== КЛАВИАТУРЫ ====================
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👔 Нужны исполнители", "🛠 Нужна работа")
    return markup


def get_subscribe_keyboard():
    markup = types.InlineKeyboardMarkup()
    channel_link = CHANNEL_ID.replace('@', '')
    markup.add(types.InlineKeyboardButton("🔗 Перейти в канал", url=f"https://t.me/{channel_link}"))
    markup.add(types.InlineKeyboardButton("✅ Я подписался", callback_data="check_sub"))
    return markup


# ==================== ПРОВЕРКА ПОДПИСКИ ====================
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"[ОШИБКА ПРОВЕРКИ ПОДПИСКИ]: {e}")
        return False


# ==================== КНОПКА "Я ПОДПИСАЛСЯ" ====================
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def handle_check_sub(call):
    if check_subscription(call.from_user.id):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅ <b>Спасибо за подписку!</b>\n\nТеперь вам доступен весь функционал бота. Нажмите /start, чтобы продолжить.",
            parse_mode="HTML"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Вы ещё не подписались на канал!", show_alert=True)


# ==================== КОМАНДА /start ====================
@bot.message_handler(commands=["start"])
def start(message):
    if not check_subscription(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Для использования бота необходимо подписаться на наш канал!</b>\n\nПодпишитесь и нажмите кнопку ниже.",
            parse_mode="HTML",
            reply_markup=get_subscribe_keyboard()
        )
        return

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


# ==================== СЦЕНАРИЙ: НУЖНЫ ИСПОЛНИТЕЛИ ====================
@bot.message_handler(func=lambda m: m.text in ["👔 Нужны исполнители", "Нужны исполнители"])
def employer(message):
    if not check_subscription(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Сначала подпишитесь на канал!</b>",
            parse_mode="HTML",
            reply_markup=get_subscribe_keyboard()
        )
        return

    instruction = "📝 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик, заполните и отправьте ответным сообщением:</b>"
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")

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


# ==================== СЦЕНАРИЙ: НУЖНА РАБОТА ====================
@bot.message_handler(func=lambda m: m.text in ["🛠 Нужна работа", "Нужна работа"])
def worker(message):
    if not check_subscription(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Сначала подпишитесь на канал!</b>",
            parse_mode="HTML",
            reply_markup=get_subscribe_keyboard()
        )
        return

    instruction = "📝 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик, заполните и отправьте ответным сообщением:</b>"
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")

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


# ==================== ОТПРАВКА ЗАЯВКИ В КАНАЛ ====================
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'voice', 'audio'])
def handle_all_messages(message):
    if message.text in ["👔 Нужны исполнители", "Нужны исполнители", "🛠 Нужна работа", "Нужна работа", "/start"]:
        return

    if not check_subscription(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Для отправки заявки необходимо быть подписанным на наш канал!</b>",
            parse_mode="HTML",
            reply_markup=get_subscribe_keyboard()
        )
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
        print(f"[ОШИБКА ОТПРАВКИ В КАНАЛ]: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при отправке. Убедитесь, что бот является администратором канала.",
            reply_markup=get_main_keyboard(),
        )


# ==================== ОБРАБОТКА ВЕБХУКА (ГЛАВНОЕ ДЛЯ VERCEL) ====================
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
    return "Bot is running on Vercel!", 200
