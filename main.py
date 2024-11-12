import telebot
import openai
from config import OpenAiKey, TgKey

openai.api_key = OpenAiKey
bot = telebot.TeleBot(TgKey)  # исправлено Telebot на TeleBot

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Привет')  # исправлено mesaage на message

@bot.message_handler(content_types=["text"])
def talk(message):
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=message.text,
        temperature=0.5,
        max_tokens=1000,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.5
    )
    gpt_text = response["choices"][0]["text"]
    bot.send_message(message.chat.id, gpt_text)

bot.polling(none_stop=True)
