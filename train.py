# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, TargetEncoder
from sklearn.model_selection import TimeSeriesSplit

import warnings
warnings.filterwarnings('ignore')

import joblib

# Подготовка данных
path = 'Stickers.csv'
df = pd.read_csv(path).dropna()
df['date'] = pd.to_datetime(df['date'])
df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
df = df.sort_values(by='date')

# Определение целевых переменных
target_columns = ['price_1', 'price_2', 'price_3', 'price_4', 'price_5', 'price_6']
X = df.drop(target_columns, axis=1)
y = df[target_columns]

# Кодирование team_name
encoder = TargetEncoder()
X['team_name_encoded'] = encoder.fit_transform(X[['team_name']], y['price_6'].values)
X = X.drop('team_name', axis=1)

# Преобразование даты
X['month'] = df['date'].dt.month
X['year'] = df['date'].dt.year
X['day'] = df['date'].dt.day
X = X.drop('date', axis=1)

# Шкалирование
scaler = StandardScaler()
numeric_cols = X.select_dtypes(include=['number']).columns
X[numeric_cols] = scaler.fit_transform(X[numeric_cols])

# Разделение данных
tscv = TimeSeriesSplit(n_splits=5)
for train_index, test_index in tscv.split(X):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

# Преобразование типов
X_train = X_train.astype(np.float32)
X_test = X_test.astype(np.float32)
y_train = y_train.astype(np.float32)
y_test = y_test.astype(np.float32)

# Обучение и оценка модели
model = RandomForestRegressor(n_estimators=1000, max_depth=8, random_state=42)

def evaluate_multioutput(model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    metrics_dict = {
        'RMSE': [],
        'MAE': [],
        'R2': []
    }

    for i in range(y_test.shape[1]):
        rmse = np.sqrt(mean_squared_error(y_test.iloc[:, i], preds[:, i]))
        mae = mean_absolute_error(y_test.iloc[:, i], preds[:, i])
        r2 = r2_score(y_test.iloc[:, i], preds[:, i])

        metrics_dict['RMSE'].append(rmse)
        metrics_dict['MAE'].append(mae)
        metrics_dict['R2'].append(r2)

    return {
        'Avg_RMSE': np.mean(metrics_dict['RMSE']),
        'Avg_MAE': np.mean(metrics_dict['MAE']),
        'Avg_R2': np.mean(metrics_dict['R2']),
        'Metrics_by_month': metrics_dict
    }

results = {}
name = 'Random Forest'
results[name] = evaluate_multioutput(model, X_train, y_train, X_test, y_test)

# Вывод результатов
results_df = pd.DataFrame({
    'Model': list(results.keys()),
    'Avg_RMSE': [v['Avg_RMSE'] for v in results.values()],
    'Avg_MAE': [v['Avg_MAE'] for v in results.values()],
    'Avg_R2': [v['Avg_R2'] for v in results.values()]
}).set_index('Model')

print(results_df.sort_values(by='Avg_RMSE'))

# Детальные метрики по месяцам для лучшей модели
best_model_name = results_df['Avg_RMSE'].idxmin()
print(f'\nДетальные метрики для {best_model_name}:')
for i, month in enumerate(['1', '2', '3', '4', '5', '6']):
    print(f'Месяц {month}:')
    print(f'RMSE: {results[best_model_name]['Metrics_by_month']['RMSE'][i]:.2f}')
    print(f'MAE: {results[best_model_name]['Metrics_by_month']['MAE'][i]:.2f}')
    print(f'R2: {results[best_model_name]['Metrics_by_month']['R2'][i]:.2f}\n')

# Сохраняем модель
joblib.dump(model, 'model.pkl')

# Сохраняем энкодер
joblib.dump(encoder, 'encoder.pkl')

# Сохраняем масштабер
joblib.dump(scaler, 'scaler.pkl')
