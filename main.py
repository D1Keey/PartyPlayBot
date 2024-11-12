import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Загрузка ключей из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Токены TELEGRAM_TOKEN и OPENAI_API_KEY должны быть установлены.")

# Инициализация OpenAI API
openai.api_key = OPENAI_API_KEY

# Создание приложения Telegram
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Flask приложение для Render
app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я бот на базе GPT. Напиши мне что-нибудь!")

async def respond_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    response = await openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_message,
        max_tokens=100,
    )
    await update.message.reply_text(response.choices[0].text.strip())

# Добавляем обработчики команд
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_user))

# Flask маршрут для проверки работы
@app.route('/')
def home():
    return "Бот работает!"

# Функция для запуска Telegram бота
def run_telegram_bot():
    application.run_polling()

# Функция для запуска Flask сервера
def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))

# Основная функция, которая запускает оба сервиса
def main():
    # Запуск Flask сервера в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Запуск Telegram бота
    run_telegram_bot()

if __name__ == '__main__':
    main()
