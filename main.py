import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai

# Загрузка ключей из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Токены TELEGRAM_TOKEN и OPENAI_API_KEY должны быть установлены.")

# Инициализация OpenAI API
openai.api_key = OPENAI_API_KEY

# Создание бота
bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание Flask приложения для приема вебхуков
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработка запросов на webhook"""
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    application.process_update(update)
    return 'OK', 200

# Запрос на создание ответа через OpenAI с новой моделью
async def respond_to_user(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    try:
        # Используем новую модель GPT
        response = await openai.Completion.create(
            model="gpt-3.5-turbo",  # Новая модель OpenAI
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

# Запуск Flask для получения webhook запросов
def run_flask():
    # Указываем порт, который Render ожидает (по умолчанию 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Запуск Telegram бота с использованием webhook
def start_telegram_bot():
    """Настроить webhook для Telegram"""
    bot.set_webhook(url=os.getenv('WEBHOOK_URL'))  # Указываем URL для webhook
    run_flask()  # Запуск Flask приложения для обработки webhook

if __name__ == "__main__":
    start_telegram_bot()
