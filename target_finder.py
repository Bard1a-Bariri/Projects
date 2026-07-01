import sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import difflib
import os
import streamlit as st

st.title("Automated Machine Learning Program")

data_source = st.text_input("Where is your data coming from?")
model_type = st.selectbox("What would you like to predict?", ["Number","Category"]).lower()
target = st.text_input("What would you like to predict?")

if st.button("Get predictions"):
    st.write("Processing data...")

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
            st.write("Unsupported file format")
            st.stop()

        st.write(f"Succesfully loaded {extension.upper()} file!")

    except Exception as e:
        st.write(f"Failed to read file. Error: {e}")



    rough_matches = difflib.get_close_matches(target, list(data.columns), n=1, cutoff=0.3)

    if not rough_matches:
        st.error("Value not found. Are you sure that's the name?")
        st.stop()
    else:
        target_column = rough_matches[0]
        data = data.dropna(subset=[target_column])
        Y = data[target_column]
   
        features_df = data.drop(columns=[target_column])
        X = pd.get_dummies(features_df, drop_first=True)
        X = X.select_dtypes(include='number')

        X = X.dropna()
        Y = Y.loc[X.index]
    
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=42, test_size = 0.2)

        if model_type == "number":
            model = RandomForestRegressor(max_depth = 7, random_state = 42, n_estimators = 200)
            model.fit(X_train, Y_train)

            predictions = model.predict(X_test)
            mae = mean_absolute_error(Y_test, predictions)

            test_results = pd.DataFrame({
                "Actual_Value": Y_test,
                "Predicted_Value": predictions
            }, index = X_test.index)

            st.subheader("Predictions Output Table")
            st.dataframe(test_results[["Actual_Value", "Predicted_Value"]].head())


        elif model_type == "category":

            model = RandomForestClassifier(max_depth = 7, random_state = 42, n_estimators = 200)
            model.fit(X_train, Y_train)

            predictions = model.predict(X_test)
            accuracy = accuracy_score(Y_test, predictions)

            test_results = pd.DataFrame({
                "Actual_Value": Y_test,
                "Predicted_Value": predictions
            }, index = X_test.index)

            st.subheader("Predictions Output Table")
            st.dataframe(test_results[["Actual_Value", "Predicted_Value"]].head())
