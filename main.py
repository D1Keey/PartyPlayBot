import os
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai
import logging

# Загрузка ключей из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Токены TELEGRAM_TOKEN и OPENAI_API_KEY должны быть установлены.")

# Инициализация OpenAI API
openai.api_key = OPENAI_API_KEY

# Создание приложения Flask
app = Flask(__name__)

# Создание бота
bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Запрос на создание ответа через OpenAI
async def respond_to_user(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    try:
        response = await openai.Completion.create(
            engine="text-davinci-003", 
            prompt=user_message, 
            max_tokens=100
        )
        await update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса.")
        logger.error(f"Ошибка OpenAI API: {e}")

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Я бот на базе GPT. Напиши мне что-нибудь!")

# Добавление обработчиков команд
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_user))

# Flask маршрут для проверки работы
@app.route('/')
def home():
    return "Бот работает!"

# Обработчик webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    application.process_update(update)
    return jsonify({"status": "ok"}), 200

# Функция для настройки webhook (асинхронная)
async def set_webhook():
    url = "https://partyplaybot.onrender.com/webhook"  # Укажите свой URL с путем
    await bot.set_webhook(url)
    print("Webhook установлен!")

# Вызов функции для установки webhook
import asyncio
asyncio.run(set_webhook())

# Функция для запуска Telegram бота с Webhook
def start_telegram_bot():
    application.run_webhook(
        listen="0.0.0.0", 
        port=int(os.getenv("PORT", 5000)), 
        url_path="webhook"  # Путь для webhook
    )

# Flask сервер для обработки запросов
def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    # Запуск Flask сервера
    run_flask()

    # Запуск Telegram бота с Webhook
    start_telegram_bot()
