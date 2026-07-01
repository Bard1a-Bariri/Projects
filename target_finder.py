import sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import difflib
import os

data_source = input("Where is your data coming from?")
model_type = input("Would you like to predict a number or a category?").strip().lower()
target = input("What would you like to predict?")

pd.set_option('display.float_format', lambda x: '%.2f' % x)

clean_path = data_source.split('?')[0]
filename, extension = os.path.splitext(clean_path)
extension = extension.lower()

try:
    if extension == '.csv':
        data = pd.read_csv(data_source)
    elif extension == '.html':
          tables = pd.read_html(data_source)
          data = tables[0]
    elif extension == '.json':
        data = pd.read_json(data_source)
    elif extension in ['.xls', '.xlsx']:
        data = pd.read_excel(data_source)
    else:
        print("Unsupported file format")
        exit()

    print(f"Succesfully loaded {extension.upper()} file!")

except Exception as e:
    print(f"Failed to read file. Error: {e}")



rough_matches = difflib.get_close_matches(target, list(data.columns), n=1, cutoff=0.3)

if not rough_matches:
    print("Value not found. Are you sure that's the name?")
else:
    target_column = rough_matches[0]
    data = data.dropna(subset=[target_column])
    Y = data[target_column]
   
    features_df = data.drop(columns=[target_column])
    X = pd.get_dummies(features_df, drop_first=True)
    X = X.select_dtypes(include='number')

    X = X.dropna()
    Y = Y.loc[X.index]
    
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=42)

    if model_type == "number":
        model = RandomForestRegressor(max_depth = 7, random_state = 42, n_estimators = 200)
        model.fit(X_train, Y_train)

        predictions = model.predict(X_test)
        mae = mean_absolute_error(Y_test, predictions)

        test_results = X_test.copy()
        test_results["ACTUAL_" + target_column] = Y_test
        test_results["PREDICTED_" + target_column] = predictions
        print("\nPredictions:")
        print(test_results[["ACTUAL_" + target_column, "PREDICTED_" + target_column]].head())


    elif model_type == "category":

        model = RandomForestClassifier(max_depth = 7, random_state = 42, n_estimators = 200)
        model.fit(X_train, Y_train)

        predictions = model.predict(X_test)
        accuracy = accuracy_score(Y_test, predictions)

        test_results = X_test.copy()
        test_results["ACTUAL_" + target_column] = Y_test
        test_results["PREDICTED_" + target_column] = predictions
        print("\nPredictions:")
        print(test_results[["ACTUAL_" + target_column, "PREDICTED_" + target_column]].head())
