import pandas as pd
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

from common.data_frame_columns import PM10, PM1, PM2_5
from common.date_time_helper import convert_to_datetime
from common.endpoints_urls import endpoints_config
from common.working_dataset_config import working_datetime, test_date_time_strings
from data_management.data_crawler import DataManager
from data_management.data_reshaper import reshape_data, prepare_dataset
from data_management.labeled_data_generator import LabeledDataGenerator, DataLabel
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

class RandomClassifier():
    def __init__(self):
        self.xdxd = DecisionTreeClassifier(random_state=0)

    def fit_data(self, labeled_data, column):
        X,y = prepare_dataset(labeled_data, column)
        self.xdxd.fit(X, y)

    def test_accuracy(self, labeled_data, column):
        X_set,y_set = prepare_dataset(labeled_data, column)
        predicted = self.xdxd.predict(X_set)
        accuracy = accuracy_score(y_set, predicted)
        print("Accuracy of KNN: ", accuracy)
        wrong_predicitons = [[DataLabel(p),DataLabel(y)] for p,y in zip(predicted, y_set) if p != y]
        print("[Predicted, Actual]")
        for error in wrong_predicitons:
            print(str(error[0]) + ", " + str(error[1]))
        return accuracy

def test():
    datas = DataManager(True).get_all_endpoints_data(endpoints_config, update=True)

    date_strings = working_datetime
    training_dates = [convert_to_datetime(date_strings[0]), convert_to_datetime(date_strings[1])]

    test_dates_string = test_date_time_strings
    test_dates = [convert_to_datetime(test_dates_string[0]), convert_to_datetime(test_dates_string[1])]

    column = PM10
    columns = [PM10, PM1, PM2_5]

    L = LabeledDataGenerator(column)
    prepared_data = L.generate_labeled_data(datas, training_dates[0], training_dates[1], 40)
    test_data = L.generate_labeled_data(datas, test_dates[0], test_dates[1], 40)
    knn = RandomClassifier()
    knn.fit_data(prepared_data, columns)
    knn.test_accuracy(test_data, columns)



if __name__ == '__main__':
    test()
