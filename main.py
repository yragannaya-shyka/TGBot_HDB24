import telebot
from telebot import types
import os
from dotenv import load_dotenv
from handlers import register_handler

load_dotenv()

token = os.getenv("BOT_API_TOKEN")

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_1 = types.KeyboardButton("Button 1")
    invite_new_user_button = types.KeyboardButton("Подключение к Битрикс24 нового сотрудника")
    access_rights_button = types.KeyboardButton("Запрос прав доступа")
    send_message_button_b24 = types.KeyboardButton("Отправить уведомление")
    keyboard.add(button_1, invite_new_user_button, access_rights_button, send_message_button_b24)
    bot.send_message(message.chat.id, 'Hello', reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_1 = types.KeyboardButton("Test button")
    keyboard.add(button_1)
    bot.send_message(message.chat.id, "Это меню помощи. Доступные команды: /start, /help, /about", reply_markup=keyboard)

register_handler(bot)


if __name__ == '__main__':
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print("Сбой сервера телеграм-бота")
