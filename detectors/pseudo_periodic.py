import numpy as np
import csv

import pandas as pd

from anomalies_simulator import AnomaliesSimulator
from data_frame_columns import PRESSURE, TIMESTAMP, TEMPERATURE, PM1
from data_manager import DataManager
from data_visualizer import display_data_frame, display_data_frames
from detectors.z_score_detector import ZScoreDetector
from endpoints_urls import endpoints_config


class PseudoPeriodicDetector():
    def detect_by_periodic_avg_network(self, datas: list[pd.DataFrame], df: pd.DataFrame, column, start_time, end_time,
                                       time_step_in_hours=1, max_depth_in_days=10, threshold=1):
        # prepare network related_data
        max_depth_time = start_time - pd.Timedelta(days=max_depth_in_days)
        filtered_datas = []

        for data in datas:
            filtered = data[(data[TIMESTAMP] >= max_depth_time) & (data[TIMESTAMP] <= start_time)]
            filtered_datas.append(filtered)

        network_data = pd.concat(filtered_datas)

        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)

        begin = start_time
        end = start_time + pd.Timedelta(hours=time_step_in_hours)

        detected_list = []
        while begin < end_time:
            # check range
            if end > end_time:
                end = end_time

            # prepare network values
            network_column_values = []
            for i in range(1, max_depth_in_days):
                network_start = begin - pd.Timedelta(days=i)
                network_end = end - pd.Timedelta(days=i)
                network_filtered = network_data[
                    (network_data[TIMESTAMP] >= network_start) & (network_data[TIMESTAMP] < network_end)]
                network_column_values.extend(network_filtered[column])

            if len(network_column_values) > 0:
                # calculate needed params
                average = np.mean(np.array(network_column_values))
                std = np.std(network_column_values)

                # filter sensor data and prepare mask
                filtered = filtered_df[(filtered_df[TIMESTAMP] >= begin) & (filtered_df[TIMESTAMP] < end)]
                values = np.array(filtered[column])
                z_scored = ((values - average) / std)
                mask = np.abs(z_scored) > threshold

                # apply mask
                detected = filtered[mask]
                detected_list.append(detected)

            begin = end
            end += pd.Timedelta(hours=time_step_in_hours)

        outliers = pd.concat(detected_list)
        outliers.name = df.name + "pseudo_periodic_avg_network"
        return outliers


def test():
    datas = DataManager(True).get_all_endpoints_data(endpoints_config, update=False)

    start_date_string = '25.11.2023 00:00'
    start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)

    end_date_string = '26.11.2023 23:59'
    end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)

    column = PM1
    display_data_frames(datas, column, start_time, end_time)

    destroyed = AnomaliesSimulator().zero_random_in_range(datas[0], column, start_time, end_time, 15)

    outliers = PseudoPeriodicDetector().detect_by_periodic_avg_network(datas[1:], destroyed, column, start_time, end_time)

    display_data_frames([destroyed, outliers], column, start_time, end_time)


if __name__ == '__main__':
    test()
