import sklearn
import pandas as pd
from sklearn import RandomForestRegresser, RandomForestClassifier
from sklearn import training_test_split
from sklearn import mean_absolute_error, accuracy_score

data_source = input("Where is your data coming from?")
model_type = input("Would you like to predict a number or a category?")
target = input("What would you like to predict?")


