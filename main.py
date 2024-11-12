import os
import logging
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

# Запрос на создание ответа через OpenAI с новой моделью
async def respond_to_user(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    try:
        # Используем модель GPT-3.5 turbo для ответа
        response = await openai.Completion.create(
            model="gpt-3.5-turbo",  # Используем новую модель
            prompt=user_message,
            max_tokens=100
        )
        await update.message.reply_text(response['choices'][0]['text'].strip())  # Исправление доступа к данным
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса.")
        logger.error(f"Ошибка OpenAI API: {e}")

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Я бот на базе GPT. Напиши мне что-нибудь!")

# Добавление обработчиков команд
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_user))

# Запуск Telegram бота с использованием polling
def start_telegram_bot():
    application.run_polling()

if __name__ == "__main__":
    # Запуск Telegram бота
    start_telegram_bot()
