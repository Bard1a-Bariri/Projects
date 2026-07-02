import xgboost as xgb
import pandas as pd

df = pd.read_csv("historical_trips.csv")

X = df[['budget', 'days', 'people', 'style_numeric']]
y = df['stayed_under_budget']

model = xgb.XGBClassifier()

model.fit(X, y)

model.save_model("predictor.json")

print("🎯 Success! 'predictor.json' has been created in your folder.")
