import numpy as np

import pandas as pd

from data_management.anomalies_simulator import AnomaliesSimulator
from common.data_frame_columns import TIMESTAMP, PM1
from data_management.data_crawler import DataManager
from common.data_visualizer import display_data_frame, display_data_frames
from common.endpoints_urls import endpoints_config

MAD_CONST = 0.6745


class ZScoreDetector:
    def detect_by_avg(self, df: pd.DataFrame, column, start_time, end_time, threshold=2):
        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)

        values = np.array(filtered_df[column])
        average = np.mean(values)
        std = np.std(values)

        # Calculate z-scores
        z_scores = ((values - average) / std)

        # Find outliers
        mask = np.abs(z_scores) > threshold

        outliers = filtered_df[mask]
        outliers.name = df.name + " ZSCORE_AVG"

        return outliers

    def detect_by_mad(self, df: pd.DataFrame, column, start_time, end_time, threshold=2):
        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)

        values = np.array(filtered_df[column])
        median = np.median(values)
        mad = 1.486 * np.median(np.abs(values - median))

        if mad == 0:
            mad = 1.253314 * np.mean(values)

        # Calculate z-scores
        modified_z_scores = ((values - median) / mad)

        # Find outliers
        mask = np.abs(modified_z_scores) > threshold

        outliers = filtered_df[mask]
        outliers.name = df.name + " ZSCORE_AVG"

        return outliers

    def detect_by_avg_network_level(self, dataframes: list[pd.DataFrame], to_detect: pd.DataFrame, column: str,
                                    start_time, end_time, threshold=2):
        network_values = np.empty(1)
        for df in dataframes:
            filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
            filtered_df = filtered_df.sort_values(by=TIMESTAMP)
            network_values = np.append(network_values, np.array(filtered_df[column]))

        filtered_df = to_detect[(to_detect[TIMESTAMP] >= start_time) & (to_detect[TIMESTAMP] <= end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)
        values = np.array(filtered_df[column])

        average = np.mean(network_values)
        std = np.std(network_values)

        # Calculate z-scores
        z_scores = ((values - average) / std)

        # Find outliers
        mask = np.abs(z_scores) > threshold

        outliers = filtered_df[mask]
        outliers.name = to_detect.name + " ZSCORE_AVG_NL"

        return outliers

    def detect_by_mad_network_level(self,dataframes: list[pd.DataFrame], to_detect: pd.DataFrame, column: str,
                                    start_time, end_time, threshold=2):

        network_values = np.empty(1)
        for df in dataframes:
            filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
            filtered_df = filtered_df.sort_values(by=TIMESTAMP)
            network_values = np.append(network_values, np.array(filtered_df[column]))

        filtered_df = to_detect[(to_detect[TIMESTAMP] >= start_time) & (to_detect[TIMESTAMP] <= end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)
        values = np.array(filtered_df[column])

        median = np.median(network_values)
        mad = 1.486 * np.median(np.abs(network_values - median))

        if mad == 0:
            mad = 1.253314 * np.mean(network_values)

        # Calculate z-scores
        z_scores = ((values - median) / mad)

        # Find outliers
        mask = np.abs(z_scores) > threshold

        outliers = filtered_df[mask]
        outliers.name = to_detect.name + " ZSCORE_MAD_NL"

        return outliers


def test():
    datas = DataManager(True).get_all_endpoints_data(endpoints_config, update=False)

    start_date_string = '10.01.2024 00:00'
    start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)

    end_date_string = '11.01.2024 23:59'
    end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)

    # display_data_frames(datas, TEMPERATURE, start_time, end_time)

    column = PM1

    display_data_frame(datas[4], column, start_time, end_time)

    # display_data_frame(datas[0], TEMPERATURE, start_time, end_time)
    destroyed_data = AnomaliesSimulator().zero_random_in_range(datas[0], column, start_time, end_time, 15)
    # display_data_frame(destroyed_data, column, start_time, end_time)

    outliers = ZScoreDetector().detect_by_mad_network_level(datas[:-1],destroyed_data, column, start_time, end_time, 1)
    display_data_frame(destroyed_data, column, start_time, end_time)

    display_data_frames([destroyed_data, outliers, datas[0]], column, start_time, end_time)
    display_data_frames(datas[:-1], column, start_time, end_time)



if __name__ == '__main__':
    test()
