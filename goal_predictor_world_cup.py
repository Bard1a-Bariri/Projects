# Import center
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Fetch the data 
df = pd.read_csv('world_cup.csv')

# Rename columns to match 
df = df.rename(columns={'GP': 'Games Played', 'G': 'Goals', 'xG': 'Expected Goals', 'S': 'Shots', 'SOG': 'Shots on Goal'})
for column in df:
  df[column] = pd.to_numeric(df[column], errors = 'coerce')
  
# Drop excess columns
df = df.dropna(subset=['Games Played', 'Expected Goals', 'Shots', 'Shots on Goal', 'Goals'])  

# Select Features (X) and Target (Y)
X = df[['Games Played', 'Expected Goals', 'Shots', 'Shots on Goal']]  
Y = df['Goals']

# Split data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Initialize and train the model
model = RandomForestRegressor(n_estimators=200, max_depth=None, min_samples_split=2, random_state=42)
model.fit(X_train, Y_train)

# Make predictions and evaluate
predictions = model.predict(X_test)
mae = mean_absolute_error(Y_test, predictions)
print(f"Mean Absolute Error: {mae:.2f} goals")

# Show the stats
test_results = X_test.copy()
test_results['Goals'] = Y_test
test_results['Predicted Goals'] = predictions.round(1)
print("\nPredictions:")
print(test_results.head())

#How important each metric was

importances = model.feature_importances_
print("\nMetric Importance\n")
ranking = list(zip(X.columns, importances))
ranking.sort(key= lambda x : x[1], reverse=True)
for name, importance in ranking:
  print(f" {name}: {importance*100:.1f}% impact")