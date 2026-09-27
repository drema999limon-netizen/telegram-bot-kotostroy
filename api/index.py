import os
from flask import Flask, request
import telebot
from telebot import types

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "8643961661:AAH9Hd5ztWytx66vZF-aQZYQxYLxAjfkhos"
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


# ==================== FLASK: ОБРАБОТКА ВЕБХУКА ====================
@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
