import random

import pandas as pd
from datetime import datetime, timezone
from data_manager import DataManager

from data_frame_columns import TIMESTAMP, PRESSURE
from endpoints_urls import endpoints_config


class AnomaliesSimulator:
    """Zeroes values in given column_name and given range [start_time, end_time]"""

    def zeros_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, value=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data.loc[:, column_name] = value
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data

    """Multiplies given column_name by scalar in range [start_time, end_time]"""

    def scaled_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, scalar=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data[column_name] *= scalar
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data

    """Adds random noise [-max_noise_value, max_noise_value] to given range [start_time, end_time]"""

    def add_random_noise_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time,
                                  max_noise_value=None) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()

        noise_length = len(selected_data)
        if max_noise_value is None:
            max_noise_value = selected_data[column_name].max()

        random_noise = [random.uniform(-max_noise_value, max_noise_value) for _ in range(noise_length)]
        # for noise in random_noise:
        #     print(noise, end=" ")

        selected_data[column_name] += random_noise
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data

    """Zeroes zeros_no values in range [start_time, end_time]"""
    def zero_random_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, zeros_no) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        length_of_selected = len(selected_data)
        column = list(selected_data[column_name])
        random_indexes = random.sample(range(length_of_selected), zeros_no)
        for index in random_indexes:
            column[index] = 0

        selected_data[column_name] = column
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data

    """Multiply random values by scalar in range [start_time, end_time]"""
    def random_scaled_values_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, changes_no, scalar) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        length_of_selected = len(selected_data)
        column = list(selected_data[column_name])
        random_indexes = random.sample(range(length_of_selected), changes_no)

        for index in random_indexes:
            column[index] *= scalar

        selected_data[column_name] = column
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data

def tests():
    datas = DataManager().get_all_endpoints_data(endpoints_config, update=False)
    date_string = '29.03.2024 13:00'

    start_time = pd.to_datetime(date_string, format='%d.%m.%Y %H:%M', utc=True)
    print(datas[0].loc[datas[0][TIMESTAMP] > start_time, PRESSURE])
    modified = AnomaliesSimulator().zero_random_in_range(datas[0], PRESSURE, start_time,
                                                              pd.to_datetime(datetime.now(), utc=True), 20)
    print(modified.loc[(modified[TIMESTAMP] > start_time) & (modified[PRESSURE] == 0), PRESSURE])

def check():
    total_elements = 100
    N = 5

    # Generate N random indexes without repetitions
    random_indexes = random.sample(range(total_elements), N)

    # Print the random indexes
    print(random_indexes)


if __name__ == '__main__':
    # check()
    tests()


