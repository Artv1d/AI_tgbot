# -*- coding: utf-8 -*-
import pandas as pd

import joblib

# Загрузка обученной модели и преобразователей
model = joblib.load('model.pkl')
encoder = joblib.load('encoder.pkl')
scaler = joblib.load('scaler.pkl')


def get_price(input_data):
    # Приведение числовых переменных к float
    for key in ['rarity', 'frequency', 'team_rating', 'starting_price']:
        input_data[key] = float(input_data[key])

    # Создаем DataFrame из входных данных
    df = pd.DataFrame([input_data], columns=[
        'team_name', 'rarity', 'date', 'frequency', 'team_rating', 'starting_price'
    ])

    # Кодирование team_name
    df['team_name_encoded'] = encoder.transform(df[['team_name']])
    df = df.drop('team_name', axis=1)

    # Преобразование даты
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['day'] = df['date'].dt.day
    df = df.drop('date', axis=1)

    # Шкалирование
    numeric_cols = ['rarity', 'frequency', 'team_rating', 'starting_price', 'team_name_encoded',
                    'month', 'year', 'day', ]
    df[numeric_cols] = scaler.transform(df[numeric_cols])

    # Предсказание
    prediction = model.predict(df)

    # Формируем результат
    months = [1, 2, 3, 4, 5, 6]
    return {f'price_{m}': round(pred, 2) for m, pred in zip(months, prediction[0])}
