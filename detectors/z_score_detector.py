import numpy as np

import pandas as pd
from matplotlib import pyplot as plt

from data_management.anomalies_simulator import AnomaliesSimulator
from common.data_frame_columns import TIMESTAMP, PM1, PM10, PM2_5
from data_management.data_crawler import DataManager
from common.data_visualizer import display_data_frame, display_data_frames
from common.endpoints_urls import endpoints_config
import matplotlib.dates as mdates

MAD_CONST = 0.6745


class ZScoreDetector:
    def detect_by_avg(self, df: pd.DataFrame, column, start_time, end_time, threshold=2):
        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)

        values = np.array(filtered_df[column])
        average = np.mean(values)
        std = np.std(values)
        if std == 0.0:
            return df

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
            if mad == 0.0:
                return df

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
        if std == 0.0:
            return to_detect

        # Calculate z-scores
        z_scores = ((values - average) / std)

        # Find outliers
        mask = np.abs(z_scores) > threshold

        outliers = filtered_df[mask]
        outliers.name = to_detect.name + " ZSCORE_AVG_NL"

        return outliers

    def detect_by_mad_network_level(self, dataframes: list[pd.DataFrame], to_detect: pd.DataFrame, column: str,
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
            if mad == 0.0:
                return to_detect

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
    display_data_frame(datas[4], PM2_5, start_time, end_time)
    display_data_frame(datas[4], PM10, start_time, end_time)

    # display_data_frame(datas[0], TEMPERATURE, start_time, end_time)
    destroyed_data = AnomaliesSimulator().zero_random_in_range(datas[0], column, start_time, end_time, 15)
    # display_data_frame(destroyed_data, column, start_time, end_time)

    outliers = ZScoreDetector().detect_by_mad_network_level(datas[:-1], destroyed_data, column, start_time, end_time, 1)
    # display_data_frame(destroyed_data, column, start_time, end_time)

    # display_data_frames([destroyed_data, outliers, datas[0]], column, start_time, end_time)
    # display_data_frames(datas[:-1], column, start_time, end_time)


def plot_example():
    def detect_by_avg_plot(self, df: pd.DataFrame, column, start_time, end_time, threshold=2):
        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)

        values = np.array(filtered_df[column])
        average = np.mean(values)
        std = np.std(values)
        if std == 0.0:
            return df

        # Calculate z-scores
        z_scores = ((values - average) / std)

        max_x = threshold * std + average
        min_x = threshold * std - average

        # Find outliers
        mask = np.abs(z_scores) > threshold

        outliers = filtered_df[mask]
        outliers.name = df.name + " ZSCORE_AVG"

        return outliers, max_x, min_x

    def display_data_frame_example(df: pd.DataFrame, column_name: str, max_x, min_x, start_time=None, end_time=None, ):
        if start_time is None:
            start_time = df[TIMESTAMP].min()

        if end_time is None:
            end_time = df[TIMESTAMP].max()

        column_name_shortened = column_name.split('.')[-1]
        print(f"Plotting {column_name_shortened} for {df.name}")
        plt.figure(figsize=(10, 8))

        y_min = float('inf')
        y_max = float('-inf')

        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
        plt.plot(filtered_df[TIMESTAMP], filtered_df[column_name], marker='.', linestyle=':', label=df.name, alpha=0.6)

        # Update min and max values
        if not filtered_df.empty:
            min_val = filtered_df[column_name].min()
            max_val = filtered_df[column_name].max()
            if min_val < y_min:
                y_min = min_val
            if max_val > y_max:
                y_max = max_val

            plt.xlabel('Date')
            plt.ylabel(column_name)
            plt.title(f'{column_name} vs. DateTime')
            plt.xticks(rotation=60)  # Rotate x-axis labels for better readability
            plt.grid(True)

            plt.axhline(y=max_x, color='r', linestyle='-', label='ZScore upper range')
            plt.axhline(y=min_x, color='r', linestyle='-', label='ZScore upper range')

            plt.legend()
            plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
            plt.show()
        else:
            print(f"No data for {df.name} for range {start_time} to {end_time}!")

    datas = DataManager(True).get_all_endpoints_data(endpoints_config, update=False)

    start_date_string = '10.03.2024 00:00'
    start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)

    end_date_string = '11.03.2024 23:59'
    end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)

    # display_data_frames(datas, TEMPERATURE, start_time, end_time)

    column = PM10

    # display_data_frame(datas[0], TEMPERATURE, start_time, end_time)
    destroyed_data = AnomaliesSimulator().zero_random_in_range(datas[0], column, start_time, end_time, 15)
    # display_data_frame(destroyed_data, column, start_time, end_time)

    outliers, max_x, min_x = detect_by_avg_plot(datas[:-1], destroyed_data, column, start_time, end_time, 3)
    display_data_frame_example(destroyed_data, column, max_x, min_x, start_time, end_time)
    display_data_frames([destroyed_data, outliers, datas[0]], column, start_time, end_time)



if __name__ == '__main__':
    test()
    # plot_example()