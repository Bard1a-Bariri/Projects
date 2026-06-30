import sklearn
import pandas as pd
from sklearn import RandomForestRegresser, RandomForestClassifier
from sklearn import training_test_split
from sklearn import mean_absolute_error, accuracy_score
import difflib
import os

data_source = input("Where is your data coming from?")
model_type = input("Would you like to predict a number or a category?")
target = input("What would you like to predict?")

filename, extension = os.path.splitext(data_source)
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

    print(f"Succesfully loaded {extension.upper()} file!")

except Exception as e:
    print(f"Failed to read file. Error: {e}")



rough_matches = difflib.get_close_matches(target, list(data.columns), n=1, cutoff=0.3)

if rough_matches not in data[columns]:
    print("Value not found. Are you sure that's the name?")
else:
    target_column = rough_matches[0]
    numeric_df = data.select_dtypes(include='number')

    X = numeric_df.drop(columns=[target_column])
    Y = numeric_df[target_column]

    X_train, X_test, Y_train, Y_test = training_test_split(X, Y, random_state=42)

    if model_type == "number":
        model = RandomForestRegresser(max_depth = 7, random_state = 42, n_estimators = 200)
        model.fit(X_train, Y_train)

        predictions = model.predict(X_test)
        mae = mean_absolute_error(Y_test, predictions)

        test_results = X_test.copy()
        test_results[rough_matches] = Y_test
        print("\nPredictions:")
        print(test_results.head())

    elif model_type == "category":

        model = RandomForestClassifier(max_depth = 7, random_state = 42, n_estimators = 200)
        model.fit(X_train, Y_train)

        predictions = model.predict(X_test)
        accuracy = accuracy_score(Y_test, predictions)

        test_results = X_test.copy()
        test_results[rough_matches] = Y_test
        print("\nPredictions:")
        print(test_results.head())
