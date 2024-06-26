from collections import Counter
from enum import Enum
import random

import numpy as np
import pandas as pd

from common.data_frame_columns import PM1, PM10, PM2_5, TIMESTAMP, ANOMALY_ENUM
from common.data_visualizer import display_data_frames, display_data_frame
from common.date_time_helper import convert_to_datetime
from common.endpoints_urls import endpoints_config
from common.working_dataset_config import working_datetime
from data_management.anomalies_simulator import AnomaliesSimulator
from data_management.data_crawler import DataManager
from detectors.pseudo_periodic import PseudoPeriodicDetector


class DataLabel(Enum):
    NORMAL = 0
    ZEROS_IN_RANGE = 1
    RANDOM_ZEROS = 2
    EXTINCTION = 3
    SCALED = 4
    NOISE = 5

    def __str__(self):
        return self.name

    def is_anomaly(self):
        return self.value > 0


def random_data_label():
    enums = list(DataLabel)
    enums = enums[1:]
    return random.choice(enums)


def should_be_anomaly(probability):
    return random.random() < (probability *1.2)


class LabeledDataGenerator:
    def __init__(self, column=PM10, value=0, scalar=10, max_noise_value=None, zeros_in_range_no=10, scaled_in_range_no=10):
        self.zeroing_value = value
        self.scalar = scalar
        self.max_noise_value = max_noise_value
        self.zeros_in_range_no = zeros_in_range_no
        self.scaled_in_range_no = scaled_in_range_no
        self.column = column

    def apply_anomaly(self, data_frame: pd.DataFrame, random_anomaly, start_time, end_time):
        match random_anomaly:
            case DataLabel.ZEROS_IN_RANGE:
                return AnomaliesSimulator().zeros_in_range(data_frame, self.column, start_time, end_time,
                                                           self.zeroing_value)
            case DataLabel.RANDOM_ZEROS:
                return AnomaliesSimulator().zero_random_in_range(data_frame, self.column, start_time, end_time,
                                                                self.zeros_in_range_no)
            case DataLabel.EXTINCTION:
                return AnomaliesSimulator().extinction_parameter_in_range(data_frame, self.column, start_time, end_time)
            case DataLabel.SCALED:
                return AnomaliesSimulator().scaled_in_range(data_frame, self.column, start_time, end_time, self.scalar)
            case DataLabel.NOISE:
                return AnomaliesSimulator().add_random_noise_in_range(data_frame, self.column, start_time, end_time,
                                                                      self.max_noise_value)

    def generate_labeled_data(self, datas: list[pd.DataFrame], start_time, end_time, anomalies_percent: float, max_anomalies = 10000000):
        # filter the data
        filtered = []
        for data in datas:
            filtered_data = data[(data[TIMESTAMP] >= start_time) & (data[TIMESTAMP] < end_time)]
            filtered_data.name = data.name
            filtered.append(filtered_data)

        # iterate day by day
        beginning = start_time
        ending = start_time + pd.Timedelta(hours=23, minutes=59, seconds=59)

        anomalies_counter = 0

        anomalies = []
        prepared_data_with_anomalies_in_days = []
        while beginning < end_time:
            if ending > end_time:
                ending = end_time

            for data in filtered:
                daily = data[(data[TIMESTAMP] >= beginning) & (data[TIMESTAMP] < ending)]
                daily.name = data.name
                if should_be_anomaly(anomalies_percent/100) and anomalies_counter<max_anomalies:
                    anomaly = random_data_label()
                    daily = self.apply_anomaly(daily, anomaly, beginning, ending)
                    # daily[ANOMALY_ENUM] = anomaly
                    anomalies_counter += 1
                else:
                    anomaly = DataLabel.NORMAL

                anomalies.append(anomaly)
                prepared_data_with_anomalies_in_days.append([daily, anomaly])


            beginning += pd.Timedelta(days=1)
            ending = beginning + pd.Timedelta(hours=23, minutes=59, seconds=59)

        print(f'Daily datas: {len(prepared_data_with_anomalies_in_days)}')
        print(f'Generated anomalies: {anomalies_counter}')

        enum_counts = Counter(anomalies)
        # Print the counts
        for label, count in enum_counts.items():
            print(f"    {label.name}: {count}")

        print("\n")

        return prepared_data_with_anomalies_in_days

        # counter = 0
        # for dataframe, anomaly in prepared_data_with_anomalies_in_days:
        #     if anomaly != DataLabel.NORMAL and counter < 10:
        #         display_data_frame(dataframe, self.column)
        #         counter+=1


def test():
    datas = DataManager(True).get_all_endpoints_data(endpoints_config, update=False)

    date_strings = working_datetime
    dates = [convert_to_datetime(date_strings[0]), convert_to_datetime(date_strings[1])]

    L = LabeledDataGenerator()
    L.generate_labeled_data(datas, dates[0], dates[1], 50)
    pass


if __name__ == '__main__':
    test()
