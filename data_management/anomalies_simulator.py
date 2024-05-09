import random

import numpy as np
import pandas as pd

from common.data_visualizer import display_data_frames
from data_management.data_crawler import DataManager

from common.data_frame_columns import TIMESTAMP, PM10
from common.endpoints_urls import endpoints_config


class AnomaliesSimulator:
    """Zeroes values in given column_name and given range [start_time, end_time]"""

    def zeros_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, value=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data.loc[:, column_name] = value
        modified_data = df.copy()
        modified_data.update(selected_data)
        modified_data.name = df.name + '_ZEROS'
        return modified_data

    """Multiplies given column_name by scalar in range [start_time, end_time]"""

    def scaled_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, scalar=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data[column_name] *= scalar
        modified_data = df.copy()
        modified_data.update(selected_data)
        modified_data.name = df.name + '_SCALED'
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
        modified_data.name = df.name + "_NOISE"
        return modified_data

    """Zeroes zeros_no values in range [start_time, end_time]"""

    def zero_random_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, zeros_no) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        length_of_selected = len(selected_data)
        column = list(selected_data[column_name])
        if length_of_selected < zeros_no:
            zeros_no = length_of_selected
        random_indexes = random.sample(range(length_of_selected), zeros_no)
        for index in random_indexes:
            column[index] = 0

        selected_data[column_name] = column
        modified_data = df.copy()
        modified_data.update(selected_data)
        modified_data.name = df.name + "_RANDOM_ZEROS"
        return modified_data

    """Multiply random values by scalar in range [start_time, end_time]"""

    def random_scaled_values_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, changes_no,
                                      scalar) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        length_of_selected = len(selected_data)
        column = list(selected_data[column_name])
        if length_of_selected < changes_no:
            changes_no = length_of_selected
        random_indexes = random.sample(range(length_of_selected), changes_no)

        for index in random_indexes:
            column[index] *= scalar

        selected_data[column_name] = column
        modified_data = df.copy()
        modified_data.update(selected_data)
        modified_data.name = df.name + '_RANDOM_SCALED'
        return modified_data

    """Simulates malfunctioning sensor, values going from 100% to 0% within given range"""

    def extinction_parameter_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time) -> pd.DataFrame:
        selected_data = df.copy()

        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        length_of_selected = len(selected_data)
        column = list(selected_data[column_name])
        linspace_array = np.linspace(0.0, 1.0, length_of_selected)

        for index in range(length_of_selected):
            column[index] *= linspace_array[index]

        selected_data[column_name] = column
        modified_data = df.copy()
        modified_data.update(selected_data)

        modified_data.name = df.name + "_EXTINCTION"

        return modified_data


def tests():
    datas = DataManager(True).get_all_endpoints_data(endpoints_config, update=False)
    date_string = '28.02.2024 00:00'
    start_time = pd.to_datetime(date_string, format='%d.%m.%Y %H:%M', utc=True)

    end_time = pd.to_datetime("28.02.2024 23:59", format='%d.%m.%Y %H:%M', utc=True)

    print(datas[0].loc[datas[0][TIMESTAMP] > start_time, PM10])
    modified1 = AnomaliesSimulator().zeros_in_range(datas[0], PM10, start_time,
                                                    end_time)
    modified2 = AnomaliesSimulator().scaled_in_range(datas[0], PM10, start_time,
                                                     end_time, 3)

    modified4 = AnomaliesSimulator().add_random_noise_in_range(datas[0], PM10, start_time, end_time)

    modified5 = AnomaliesSimulator().zero_random_in_range(datas[0], PM10, start_time,
                                                          end_time, 20)
    modified6 = AnomaliesSimulator().random_scaled_values_in_range(datas[0], PM10, start_time,
                                                                   end_time, 20, 3)

    modified7 = AnomaliesSimulator().extinction_parameter_in_range(datas[0], PM10, start_time, end_time)

    display_data_frames([modified1, modified2, modified4, modified5, modified6, modified7, datas[0]], PM10, start_time,
                        end_time)


def check():
    # Define the number of steps
    N = 10  # Change this to the desired number of steps

    # Generate the linspace array
    linspace_array = np.linspace(1.0, 0.0, N)

    # Print the generated array
    print(linspace_array)


if __name__ == '__main__':
    # check()
    tests()
