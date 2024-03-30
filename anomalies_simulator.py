import random

import pandas as pd
from datetime import datetime, timezone
from data_manager import DataManager

from data_frame_columns import TIMESTAMP, PRESSURE
from endpoints_urls import endpoints_config


class AnomaliesSimulator:

    def zeros_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, value=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data.loc[:, column_name] = value
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data

    def scaled_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, scalar=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data[column_name] *= scalar
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data

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


def tests():
    datas = DataManager().get_all_endpoints_data(endpoints_config, update=True)
    date_string = '21.03.2024 13:00'

    start_time = pd.to_datetime(date_string, format='%d.%m.%Y %H:%M', utc=True)
    print(datas[0].loc[datas[0][TIMESTAMP] > start_time, PRESSURE])
    modified = AnomaliesSimulator().add_random_noise_in_range(datas[0], PRESSURE, start_time,
                                                    pd.to_datetime(datetime.now(), utc=True))
    print(modified.loc[modified[TIMESTAMP] > start_time, PRESSURE])


if __name__ == '__main__':
    tests()
