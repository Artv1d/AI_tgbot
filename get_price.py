# -*- coding: windows-1251 -*-
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, TargetEncoder
import joblib

# Загрузка обученной модели и преобразователей
model = joblib.load('sticker_price_model.pkl')
encoder = joblib.load('team_encoder.pkl')
scaler = joblib.load('scaler.pkl')

def get_price(input_data):
    # Создаем DataFrame из входных данных
    df = pd.DataFrame([input_data], columns=[
        'team_name', 'rarity', 'date', 'frequency', 'team_rating', 'starting_price'
    ])

    # Кодирование team_name
    df['team_name_encoded'] = encoder.transform(df[['team_name']])
    df = df.drop('team_name', axis=1)
    
    # Преобразование даты
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['day'] = df['date'].dt.day
    df = df.drop('date', axis=1)

    # Масштабирование
    numeric_cols = ['rarity', 'frequency', 'team_rating', 'starting_price', 'team_name_encoded',
                    'month', 'year', 'day', ]
    df[numeric_cols] = scaler.transform(df[numeric_cols])   
    # Предсказание
    prediction = model.predict(df)
    
    # Формируем результат
    months = [1, 2, 3, 4, 5, 6]
    return {f'month_{m}': round(pred, 2) for m, pred in zip(months, prediction[0])}

# Пример использования
input_data = {
    'team_name': 'FaZe Clan',
    'rarity': 4,
    'date': '2023-06-24',
    'frequency': 1,
    'team_rating': 1,
    'starting_price': 1000
}

predictions = get_price(input_data)
print("Прогнозные цены:")
for month, price in predictions.items():
    print(f"{month}: {price}")