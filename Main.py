import os
import re
import sqlite3
import random
import calendar

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
    try:
        if message.content_type != 'text':
            raise ValueError("Пожалуйста, введите текст.")
        input_data["team_name"] = message.text.strip()
        bot.send_message(message.chat.id,"Введите, пожалуйста, цифру rarity стикера\n"
                                          "1 - default, 2 - glitter, 3 - holo, 4 - gold\n",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_rarity)

    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПожалуйста, введите название команды текстом.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_team_name)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла непредвиденная ошибка: {e}\nПопробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_team_name)

def get_rarity(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Пожалуйста, введите текст.")
        rarity = int(message.text.strip())
        if not 1 <= rarity <= 4:
            raise ValueError("Rarity должна быть цифрой от 1 до 4.")
        input_data["rarity"] = rarity
        bot.send_message(message.chat.id, "Введите, пожалуйста, дату ивента в формате ДД.ММ.ГГГГ\n"
                                          "Пример: 08.06.2005\n",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_data)

    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПожалуйста, введите цифру от 1 до 4.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_rarity)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла непредвиденная ошибка: {e}\nПопробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_rarity)

def get_data(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Пожалуйста, введите текст.")
        date_str = message.text.strip()
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_str):
            raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

        day, month, year = map(int, date_str.split('.'))

        # Проверка на валидность дня и месяца с учетом високосного года
        if not (1 <= month <= 12):
            raise ValueError("Неверный месяц. Месяц должен быть от 1 до 12.")

        max_days = calendar.monthrange(year, month)[1]  # Получаем количество дней в месяце
        if not (1 <= day <= max_days):
            raise ValueError(f"Неверный день для месяца {month}. В этом месяце {max_days} дней.")


        input_data["date"] = date_str
        bot.send_message(message.chat.id, "Введите, пожалуйста, коэффициент получения наклеек командой\n"
                                          "0-10 штук: 1, 10-30 штук: 2, 30+ штук: 3\n",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_frequency)

    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПожалуйста, введите дату в формате ДД.ММ.ГГГГ.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_data)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла непредвиденная ошибка: {e}\nПопробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_data)

def get_frequency(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Пожалуйста, введите текст.")
        frequency = int(message.text.strip())
        if not 1 <= frequency <= 3:
            raise ValueError("Коэффициент получения должен быть цифрой от 1 до 3.")
        input_data["frequency"] = frequency
        bot.send_message(message.chat.id, "Введите, пожалуйста, рейтинг популярности команды\n"
                                          "нави, фэйз, фурия, вп, фнатик, спирит, ликвид, виталити, нип, г2, астралис: 1\n"
                                          "с9, хироик, мауз, энс, биг, гамбит: 2\n"
                                          "спраут, бне, кпф, энтропик, ег, монте, гл, апекс, итб, найн: 3\n",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_team_rating)

    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПожалуйста, введите цифру от 1 до 3.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_frequency)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла непредвиденная ошибка: {e}\nПопробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_frequency)

def get_team_rating(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Пожалуйста, введите текст.")
        team_rating = int(message.text.strip())
        if not 1 <= team_rating <= 3:
            raise ValueError("Рейтинг команды должен быть цифрой от 1 до 3.")
        input_data["team_rating"] = team_rating
        bot.send_message(message.chat.id, "Введите, пожалуйста, стартовую цену стикера в рублях\n"
                                          "Пример: 100\n",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_starting_price)

    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПожалуйста, введите цифру от 1 до 3.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_team_rating)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла непредвиденная ошибка: {e}\nПопробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_team_rating)

def get_starting_price(message):
    try:
        if message.content_type != 'text':
            raise ValueError("Пожалуйста, введите текст.")
        starting_price = float(message.text.strip())
        if starting_price <= 0:
            raise ValueError("Стартовая цена должна быть больше 0.")
        input_data["starting_price"] = starting_price
        print (input_data)
        bot.send_message(message.chat.id, f"Прогнозируемая цена через 1 месяц: {get_price.get_price(input_data)['price_1']} ₽\n"
                                               f"Прогнозируемая цена через 2 месяца: {get_price.get_price(input_data)['price_2']} ₽\n"
                                               f"Прогнозируемая цена через 3 месяца: {get_price.get_price(input_data)['price_3']} ₽\n"
                                               f"Прогнозируемая цена через 4 месяца: {get_price.get_price(input_data)['price_4']} ₽\n"
                                               f"Прогнозируемая цена через 5 месяцев: {get_price.get_price(input_data)['price_5']} ₽\n"
                                               f"Прогнозируемая цена через 6 месяцев: {get_price.get_price(input_data)['price_6']} ₽\n")

    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПожалуйста, введите число больше 0.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_starting_price)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла непредвиденная ошибка: {e}\nПопробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_starting_price)

if __name__ == "__main__":
    bot.polling(none_stop=True)
