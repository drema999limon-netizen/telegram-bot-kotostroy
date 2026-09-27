import os
import html
from flask import Flask, request
import telebot
from telebot import types

# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ ВПИШИТЕ СВОИ ДАННЫЕ ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼

# ID канала, на который нужно подписаться (вида "-1001234567890")
DEFAULT_SUBSCRIBE_CHANNEL_ID = ""

# ID закрытого канала, куда приходят заявки (вида "-1002345678901")
DEFAULT_APPLICATIONS_CHANNEL_ID = ""

# Ссылка на канал для кнопки «Перейти в канал»
DEFAULT_SUBSCRIBE_CHANNEL_LINK = "https://t.me/+D_-gQTBazPc2ZTMy"

# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲


# ==================== НАСТРОЙКИ (менять не нужно) ====================

def env(name, default=""):
    """Берёт значение из Vercel, а если его нет — значение из кода"""
    return (os.environ.get(name, "") or "").strip() or default

# Токен бота — ТОЛЬКО в Vercel → Environment Variables → BOT_TOKEN
BOT_TOKEN = env("BOT_TOKEN")

# Ваш личный ID — сюда придёт заявка, если в канал отправить не получилось
ADMIN_ID = env("-1004411619465")

SUBSCRIBE_CHANNEL_ID = env("SUBSCRIBE_CHANNEL_ID", DEFAULT_SUBSCRIBE_CHANNEL_ID)
SUBSCRIBE_CHANNEL_LINK = env("SUBSCRIBE_CHANNEL_LINK", DEFAULT_SUBSCRIBE_CHANNEL_LINK)
APPLICATIONS_CHANNEL_ID = env("APPLICATIONS_CHANNEL_ID", DEFAULT_APPLICATIONS_CHANNEL_ID)

BTN_EMPLOYER = "👔 Нужны исполнители"
BTN_WORKER = "🛠 Нужна работа"
MENU_BUTTONS = [BTN_EMPLOYER, "Нужны исполнители", BTN_WORKER, "Нужна работа"]

bot = telebot.TeleBot(BOT_TOKEN or "0:missing", threaded=False)
app = Flask(__name__)


# ==================== КЛАВИАТУРЫ ====================

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BTN_EMPLOYER, BTN_WORKER)
    return markup


def get_subscribe_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Перейти в канал", url=SUBSCRIBE_CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
    return markup


# ==================== ПРОВЕРКА ПОДПИСКИ ====================

def check_subscription(user_id):
    """True — пользователь подписан на канал"""
    if not SUBSCRIBE_CHANNEL_ID:
        print("ВНИМАНИЕ: не задан ID канала для подписки — проверка отключена")
        return True
    try:
        member = bot.get_chat_member(SUBSCRIBE_CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        if member.status == "restricted" and getattr(member, "is_member", False):
            return True
        return False
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False


def send_subscribe_required(chat_id):
    text = (
        "🔒 <b>Для использования бота необходимо подписаться на наш канал!</b>\n\n"
        "1️⃣ Нажмите кнопку «Перейти в канал» и подпишитесь\n"
        "2️⃣ Вернитесь сюда и нажмите «Я подписался»"
    )
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=get_subscribe_keyboard())


def send_welcome(chat_id, user_name, after_subscribe=False):
    name = html.escape(user_name or "")
    if after_subscribe:
        first_line = "🎉 <b>Отлично, подписка подтверждена!</b>"
    else:
        first_line = f"👋 <b>Здравствуйте, {name}!</b>"
    text = (
        f"{first_line}\n\n"
        f"Добро пожаловать в сервис поиска работы и исполнителей <b>Kotostroy!</b> 🏗✨\n\n"
        f"Пожалуйста, выберите нужный вариант ниже 👇"
    )
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=get_main_keyboard())


# ==================== СЛУЖЕБНЫЕ СТРАНИЦЫ ====================

@app.route("/debug", methods=["GET"])
def debug():
    """Диагностика: https://ваш-адрес.vercel.app/debug"""
    lines = [
        f"BOT_TOKEN задан: {'да' if BOT_TOKEN else 'НЕТ'}",
        f"ADMIN_ID задан: {'да' if ADMIN_ID else 'НЕТ'}",
        f"Канал для подписки: {SUBSCRIBE_CHANNEL_ID or 'НЕ ЗАДАН (проверка подписки отключена)'}",
        f"Ссылка на канал: {SUBSCRIBE_CHANNEL_LINK}",
        f"Канал для заявок: {APPLICATIONS_CHANNEL_ID or 'НЕ ЗАДАН (заявки идут в личку ADMIN_ID)'}",
    ]

    if not BOT_TOKEN:
        return "<br>".join(lines)

    try:
        me = bot.get_me()
        lines.append(f"Токен рабочий, бот: @{me.username}")
    except Exception as e:
        lines.append(f"Ошибка токена: {e}")
        return "<br>".join(lines)

    try:
        info = bot.get_webhook_info()
        lines.append(f"Webhook URL: {info.url or 'НЕ УСТАНОВЛЕН — откройте /set_webhook'}")
        lines.append(f"Ожидающих сообщений: {info.pending_update_count}")
        lines.append(f"Последняя ошибка: {info.last_error_message or 'нет'}")
    except Exception as e:
        lines.append(f"Ошибка webhook: {e}")

    if SUBSCRIBE_CHANNEL_ID:
        try:
            member = bot.get_chat_member(SUBSCRIBE_CHANNEL_ID, me.id)
            lines.append(f"Статус бота в канале для подписки: {member.status}")
        except Exception as e:
            lines.append(f"Канал для подписки: ошибка — {e}")

    if APPLICATIONS_CHANNEL_ID:
        try:
            member = bot.get_chat_member(APPLICATIONS_CHANNEL_ID, me.id)
            can_post = getattr(member, "can_post_messages", None)
            lines.append(f"Статус бота в канале для заявок: {member.status}")
            if member.status == "administrator" and can_post is False:
                lines.append("⚠️ У бота нет права «Публикация сообщений» в канале для заявок")
        except Exception as e:
            lines.append(f"Канал для заявок: ошибка — {e}")

    return "<br>".join(lines)


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Установка webhook: https://ваш-адрес.vercel.app/set_webhook"""
    if not BOT_TOKEN:
        return "BOT_TOKEN не задан в Vercel", 200
    url = "https://" + request.host + "/"
    try:
        bot.remove_webhook()
        ok = bot.set_webhook(url=url, drop_pending_updates=True)
        return f"Webhook {'установлен' if ok else 'НЕ установлен'}: {url}", 200
    except Exception as e:
        return f"Ошибка установки webhook: {e}", 200


# ==================== ПРИЁМ СООБЩЕНИЙ ОТ TELEGRAM ====================

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def catch_all(path):
    if request.method == "POST":
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                json_string = request.get_data().decode("utf-8")
                update = telebot.types.Update.de_json(json_string)
                bot.process_new_updates([update])
            except Exception as e:
                print(f"Ошибка обработки апдейта: {e}")
            return "OK", 200
        return "Forbidden", 403
    return "Bot is running!", 200


# ==================== /start ====================

@bot.message_handler(commands=["start"])
def start(message):
    if not check_subscription(message.from_user.id):
        send_subscribe_required(message.chat.id)
        return
    send_welcome(message.chat.id, message.from_user.first_name)


# ==================== КНОПКА «Я ПОДПИСАЛСЯ» ====================

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def handle_check_subscription(call):
    chat_id = call.message.chat.id
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
        try:
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        except Exception:
            pass
        send_welcome(chat_id, call.from_user.first_name, after_subscribe=True)
    else:
        bot.answer_callback_query(
            call.id,
            "❌ Вы ещё не подписались! Подпишитесь и попробуйте снова.",
            show_alert=True,
        )


# ==================== «НУЖНЫ ИСПОЛНИТЕЛИ» ====================

@bot.message_handler(func=lambda m: m.text in [BTN_EMPLOYER, "Нужны исполнители"])
def employer(message):
    chat_id = message.chat.id
    if not check_subscription(message.from_user.id):
        send_subscribe_required(chat_id)
        return

    bot.send_message(
        chat_id,
        "📝 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик, "
        "заполните и отправьте ответным сообщением:</b>",
        parse_mode="HTML",
    )
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
    bot.send_message(chat_id, template, parse_mode="HTML")


# ==================== «НУЖНА РАБОТА» ====================

@bot.message_handler(func=lambda m: m.text in [BTN_WORKER, "Нужна работа"])
def worker(message):
    chat_id = message.chat.id
    if not check_subscription(message.from_user.id):
        send_subscribe_required(chat_id)
        return

    bot.send_message(
        chat_id,
        "📝 <b>Нажмите на текст ниже, чтобы скопировать его в 1 клик, "
        "заполните и отправьте ответным сообщением:</b>",
        parse_mode="HTML",
    )
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
    bot.send_message(chat_id, template, parse_mode="HTML")


# ==================== ЗАЯВКИ → В КАНАЛ ДЛЯ ЗАЯВОК ====================

def deliver(target, user_info, from_chat_id, message_id):
    """Отправляет шапку заявки и саму заявку в указанный чат"""
    bot.send_message(target, user_info, parse_mode="HTML")
    bot.copy_message(target, from_chat_id, message_id)


@bot.message_handler(content_types=["text", "photo", "video", "document", "voice", "audio"])
def handle_all_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Кнопки меню и команды не пересылаем
    if message.text and (message.text in MENU_BUTTONS or message.text.startswith("/")):
        return

    if not check_subscription(user_id):
        send_subscribe_required(chat_id)
        return

    username = message.from_user.username
    first_name = html.escape(message.from_user.first_name or "")
    username_text = f"@{username}" if username else "Скрыт"

    user_info = (
        f"🔔 <b>НОВАЯ ЗАЯВКА ИЗ БОТА</b> 🔔\n\n"
        f"👤 <b>От кого:</b> {username_text} ({first_name})\n"
        f"🆔 <b>ID клиента:</b> <code>{user_id}</code>\n"
        f"👇 <b>Содержимое заявки:</b> 👇"
    )

    target = APPLICATIONS_CHANNEL_ID or ADMIN_ID
    if not target:
        print("ВНИМАНИЕ: не задан ни канал для заявок, ни ADMIN_ID")
        bot.send_message(chat_id, "❌ Бот временно не принимает заявки. Попробуйте позже.")
        return

    delivered = False
    try:
        deliver(target, user_info, chat_id, message.message_id)
        delivered = True
    except Exception as e:
        print(f"Ошибка отправки заявки в {target}: {e}")
        # Запасной вариант: заявка вам в личку с причиной ошибки
        if ADMIN_ID and str(target) != str(ADMIN_ID):
            try:
                bot.send_message(
                    ADMIN_ID,
                    f"⚠️ <b>Не удалось отправить заявку в канал</b> "
                    f"<code>{html.escape(str(target))}</code>\n"
                    f"Причина: <code>{html.escape(str(e))}</code>\n\n"
                    f"Заявка ниже 👇",
                    parse_mode="HTML",
                )
                deliver(ADMIN_ID, user_info, chat_id, message.message_id)
                delivered = True
            except Exception as e2:
                print(f"Ошибка отправки заявки админу: {e2}")

    if delivered:
        bot.send_message(
            chat_id,
            "✅ <b>Отлично!</b> Ваша заявка успешно отправлена.\nСкоро мы с вами свяжемся!",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
    else:
        bot.send_message(
            chat_id,
            "❌ Произошла ошибка при отправке заявки. Попробуйте позже.",
            reply_markup=get_main_keyboard(),
        )
