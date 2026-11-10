import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import numpy as np
import math

url = "https://raw.githubusercontent.com/plotly/datasets/master/stockdata.csv"

df = pd.read_csv(url, parse_dates=['Date'], index_col = 'Date')

predictions_dict = {}
mae_dict = {}
direction_dict = {}
model = LinearRegression()
scaler = StandardScaler()
for comp in df.columns:
  temp_df = pd.DataFrame()
  temp_df["Target_Change"] = df[comp].diff()
  temp_df["change_lag_1"] = temp_df["Target_Change"].shift(1)
  temp_df["change_lag_2"] = temp_df["Target_Change"].shift(2)
  temp_df["change_vol_10"] = temp_df["Target_Change"].rolling(10).std()
  temp_df = temp_df.dropna()
  X = temp_df[["change_lag_1", "change_lag_2", "change_vol_10"]]
  Y = temp_df["Target_Change"]
  split_idx = int(len(temp_df)*0.8)
  X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
  Y_train, Y_test = Y.iloc[:split_idx], Y.iloc[split_idx:]
  X_train_scale = scaler.fit_transform(X_train)
  X_test_scale = scaler.transform(X_test)
  model.fit(X_train_scale, Y_train)
  preds = model.predict(X_test_scale)
  mae = mean_absolute_error(preds, Y_test)
  direction_correct = np.sign(preds) == np.sign(Y_test.values)
  dir_acc = np.mean(direction_correct) * 100
  direction_dict[comp] = round(dir_acc, 2)
  mae_dict[comp] = round(mae, 2)
  predictions_dict[comp] = preds
results = pd.DataFrame(predictions_dict)
mae_df = pd.DataFrame(mae_dict, index=["MAE"])
direc_df = pd.DataFrame(direction_dict, index=["Accuracy"])
fig, ax = plt.subplots()
ax.set_xlim(0, len(Y_test))
y_min = math.floor(min(Y_test.min(), preds.min()))
y_max = math.ceil(max(Y_test.max(), preds.max()))
ax.set_ylim(y_min, y_max)
ax.plot(Y_test.values, label="Actual", color="red", linewidth = 2)
ax.plot(preds, label="Predicted", color="blue", linewidth = 2)
ax.set_xlabel("Time increase")
ax.set_ylabel("Value")
ax.legend()

plt.show()
print(mae_df)
print(direc_df)

