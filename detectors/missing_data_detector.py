import csv

import pandas as pd

from anomalies_simulator import AnomaliesSimulator
from data_frame_columns import PRESSURE, TIMESTAMP
from data_manager import DataManager
from data_visualizer import display_data_frame
from endpoints_urls import endpoints_config

MEASUREMENT_PERIOD = 3600
FILENAME_PREFIX = '../missing_data_detected/'


class MissingDataDetector:

    def detect_missing_data(self, df: pd.DataFrame, start_time=None, end_time=None,
                            measurement_period=MEASUREMENT_PERIOD):
        if start_time is None:
            start_time = df[TIMESTAMP].min()
        if end_time is None:
            end_time = df[TIMESTAMP].max()

        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
        filtered_df = filtered_df.sort_values(by=[TIMESTAMP])

        prev_dateTime = filtered_df[TIMESTAMP].min()
        time_diff_list = []

        for index, row in filtered_df.iterrows():
            curr_dateTime = row[TIMESTAMP]
            time_diff = curr_dateTime - prev_dateTime
            time_diff_list.append([prev_dateTime, curr_dateTime, time_diff])
            prev_dateTime = curr_dateTime

        result = [x for x in time_diff_list if x[2].seconds > measurement_period]

        return result


def save_list_of_lists_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"CSV file '{filename}' has been created successfully.")


def test():
    datas = DataManager().get_all_endpoints_data(endpoints_config, update=False)
    start_date_string = '02.04.2022 00:00'
    start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)

    end_date_string = '02.04.2023 23:59'
    end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)

    # display_data_frame(datas[1], PM10, start_time, end_time)
    # display_data_frame(datas[2], PM10, start_time, end_time)

    # display_data_frame(datas[0], PRESSURE, start_time, end_time)
    # destroyed_data = AnomaliesSimulator().zero_random_in_range(datas[0], PRESSURE, start_time, end_time, 10)
    # display_data_frame(destroyed_data, PRESSURE, start_time, end_time)

    for data in datas:
        missing_data = MissingDataDetector().detect_missing_data(data)
        if len(missing_data) > 0:
            save_list_of_lists_to_csv(missing_data, filename=(FILENAME_PREFIX + data.name + ".csv"))


if __name__ == '__main__':
    test()
