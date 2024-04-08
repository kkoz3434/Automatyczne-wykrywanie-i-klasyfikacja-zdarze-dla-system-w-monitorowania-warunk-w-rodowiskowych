import random

import numpy as np
import pandas as pd
from datetime import datetime, timezone

from anomalies_simulator import AnomaliesSimulator
from data_manager import DataManager
import matplotlib.pyplot as plt
from data_frame_columns import TIMESTAMP, PRESSURE, TEMPERATURE, PM10, PM2_5, PM1
from endpoints_urls import endpoints_config
import matplotlib.dates as mdates


def display_data_frame(df: pd.DataFrame, column_name: str, start_time, end_time):
    column_name_shortened = column_name.split('.')[-1]
    print(f"Plotting {column_name_shortened} for {df.name}")
    plt.figure(figsize=(10,6))

    y_min = float('inf')
    y_max = float('-inf')

    filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
    plt.plot(filtered_df[TIMESTAMP], filtered_df[column_name], marker='o', linestyle='', label=df.name)

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
        plt.legend()
        plt.title(f'{column_name} vs. DateTime')
        plt.xticks(rotation=60)  # Rotate x-axis labels for better readability
        plt.grid(True)
        plt.ylim(0.9 * y_min, 1.1 * y_max)

        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.show()
    else:
        print(f"No data for {df.name} for range {start_time} to {end_time}!")


def display_data_frames(dataframes: list[pd.DataFrame], column_name: str, start_time, end_time, ):
    # Plot the data
    plt.figure(figsize=(10,6))

    y_min = float('inf')
    y_max = float('-inf')

    for df in dataframes:
        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] <= end_time)]
        plt.plot(filtered_df[TIMESTAMP], filtered_df[column_name], marker='.', linestyle='', label=df.name)

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
    plt.legend()
    plt.title(f'{column_name} vs. DateTime')
    plt.xticks(rotation=90, ha='right')  # Rotate x-axis labels for better readability
    plt.grid(True)
    plt.ylim(0.9 * y_min, 1.1 * y_max)

    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.show()


def test():
    datas = DataManager().get_all_endpoints_data(endpoints_config, update=False)
    start_date_string = '30.12.2022 00:00'
    start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)

    end_date_string = '01.01.2023 23:59'
    end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)

    # display_data_frame(datas[1], PM10, start_time, end_time)
    # display_data_frame(datas[2], PM10, start_time, end_time)

    # display_data_frame(datas[0], PRESSURE, start_time, end_time)
    # destroyed_data = AnomaliesSimulator().zero_random_in_range(datas[0], PRESSURE, start_time, end_time, 10)
    # display_data_frame(destroyed_data, PRESSURE, start_time, end_time)

    display_data_frames(datas, PM1, start_time, end_time)


if __name__ == '__main__':
    test()
    pass
