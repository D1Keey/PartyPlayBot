import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, Application
import openai

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки для OpenAI и Telegram
OPENAI_API_KEY = "your-openai-api-key"
TELEGRAM_TOKEN = "your-telegram-bot-token"
openai.api_key = OPENAI_API_KEY

# Инициализация Telegram бота
bot = Bot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот, который использует OpenAI.")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context):
    user_message = update.message.text
    response = openai.Completion.create(
        model="gpt-3.5-turbo",  # Обновите модель на актуальную, если нужно
        prompt=user_message,
        max_tokens=150
    )
    answer = response.choices[0].text.strip()
    await update.message.reply_text(answer)

# Создаем приложение Telegram
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Добавляем обработчики команд и сообщений
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    # Обрабатываем входящие сообщения
    json_str = request.get_data().decode("UTF-8")
    try:
        update = Update.de_json(json_str, bot)
        application.update_queue.put(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return "Error", 500

if __name__ == "__main__":
    # Настройка порта
    port = int(os.getenv("PORT", 5000))  # Используем переменную окружения PORT для Render
    # Запуск Flask-приложения
    app.run(host="0.0.0.0", port=port)
