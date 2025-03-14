import os
import re
import sqlite3
import random

import telebot
from telebot import types

import config

bot = telebot.TeleBot(config.TOKEN)
bot.set_webhook()

@bot.message_handler(commands=['start', 'main', 'hello'])
@bot.message_handler(func=lambda message: message.text.lower() == 'главная')
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Получить прогноз на скин")
    markup.row(btn1)

    bot.send_message(message.chat.id,
                     "Нажмите на кнопку <b><u>получить прогноз на скин</u></b>, после чего внесите все необходимые данные",
                     parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['get'])
@bot.message_handler(func=lambda message: message.text.lower() == 'получить прогноз на скин')
def get(message):
    bot.send_message(message.chat.id, "Введите, пожалуйста, название товара",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    if message.content_type == 'text':
        global name_product
        name_product = message.text.strip()
    bot.send_message(message.chat.id, f"Прогнозируемая цена скина *{name_product}*: {random.randint(1, 10000000)} ₽")

if __name__ == "__main__":
    bot.polling(none_stop=True)
