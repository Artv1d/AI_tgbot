import os
import re
import sqlite3
import random

import telebot
from telebot import types

import config
import get_price

bot = telebot.TeleBot(config.TOKEN)
bot.set_webhook()

input_data = {
    'team_name': 'FaZe Clan',
    'rarity': 4,
    'date': '2023-06-24',
    'frequency': 1,
    'team_rating': 1,
    'starting_price': 8.8
}

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
    bot.send_message(message.chat.id, "Введите, пожалуйста, название команды стикера\n"
                                           "Пример ввода: FaZe Clan\n",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_team_name)

def get_team_name(message):
    if message.content_type == 'text':
        input_data["team_name"] = message.text.strip()
    bot.send_message(message.chat.id,"Введите, пожалуйста, цифру rarity стикера\n"
                                      "1 - default, 2 - glitter, 3 - holo, 4 - gold\n",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_rarity)

def get_rarity(message):
    if message.content_type == 'text':
        input_data["rarity"] = message.text.strip()
    bot.send_message(message.chat.id, "Введите, пожалуйста, дату ивента в формате ДД.ММ.ГГГГ\n"
                                      "Пример: 08.06.2005\n",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_data)

def get_data(message):
    if message.content_type == 'text':
        input_data["date"] = message.text.strip()
    bot.send_message(message.chat.id, "Введите, пожалуйста, коэффициент получения наклеек командой\n"
                                      "0-10 штук: 1, 10-30 штук: 2, 30+ штук: 3\n",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_frequency)

def get_frequency(message):
    if message.content_type == 'text':
        input_data["frequency"] = message.text.strip()
    bot.send_message(message.chat.id, "Введите, пожалуйста, рейтинг популярности команды\n"
                                      "нави, фэйз, фурия, вп, фнатик, спирит, ликвид, виталити, нип, г2, астралис: 1\n"
                                      "с9, хироик, мауз, энс, биг, гамбит: 2\n"
                                      "спраут, бне, кпф, энтропик, ег, монте, гл, апекс, итб, найн: 3\n",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_team_rating)

def get_team_rating(message):
    if message.content_type == 'text':
        input_data["team_rating"] = message.text.strip()
    bot.send_message(message.chat.id, "Введите, пожалуйста, стартовую цену стикера в рублях\n"
                                      "Пример: 100\n",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_starting_price)

def get_starting_price(message):
    if message.content_type == 'text':
        input_data["starting_price"] = message.text.strip()
    print (input_data)
    bot.send_message(message.chat.id, f"Прогнозируемая цена скина: {get_price.get_price(input_data)["price_6"]} ₽")

if __name__ == "__main__":
    bot.polling(none_stop=True)
