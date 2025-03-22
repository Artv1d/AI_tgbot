# -*- coding: windows-1251 -*-
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, TargetEncoder
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

import joblib

path = 'StickerBot/Stickers.csv'
df = pd.read_csv(path).dropna()
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by='date')

target_columns = ['price_1', 'price_2', 'price_3', 'price_4', 'price_5', 'target_price']
X = df.drop(target_columns, axis=1)
y = df[target_columns]

encoder = TargetEncoder()
X['team_name_encoded'] = encoder.fit_transform(X[['team_name']], y['target_price'].values)
X = X.drop('team_name', axis=1)

X['month'] = df['date'].dt.month
X['year'] = df['date'].dt.year
X['day'] = df['date'].dt.day
X = X.drop('date', axis=1)

scaler = StandardScaler()
numeric_cols = X.select_dtypes(include=['number']).columns
X[numeric_cols] = scaler.fit_transform(X[numeric_cols])

tscv = TimeSeriesSplit(n_splits=5)
for train_index, test_index in tscv.split(X):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

X_train = X_train.astype(np.float32)
X_test = X_test.astype(np.float32)

y_train = y_train.astype(np.float32)
y_test = y_test.astype(np.float32)

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

# ����� �����������
results_df = pd.DataFrame({
    'Model': list(results.keys()),
    'Avg_RMSE': [v['Avg_RMSE'] for v in results.values()],
    'Avg_MAE': [v['Avg_MAE'] for v in results.values()],
    'Avg_R2': [v['Avg_R2'] for v in results.values()]
}).set_index('Model')

print(results_df.sort_values(by='Avg_RMSE'))

# ��������� ������� �� ������� ��� ������ ������
best_model_name = results_df['Avg_RMSE'].idxmin()
print(f'\n��������� ������� ��� {best_model_name}:')
for i, month in enumerate(['1', '2', '3', '4', '5', '6']):
    print(f'����� {month}:')
    print(f'RMSE: {results[best_model_name]['Metrics_by_month']['RMSE'][i]:.2f}')
    print(f'MAE: {results[best_model_name]['Metrics_by_month']['MAE'][i]:.2f}')
    print(f'R2: {results[best_model_name]['Metrics_by_month']['R2'][i]:.2f}\n')

# ��������� ������
joblib.dump(model, 'sticker_price_model.pkl')

# ��������� �������
joblib.dump(encoder, 'team_encoder.pkl')

# ��������� ���������
joblib.dump(scaler, 'scaler.pkl')