import pandas as pd

from data_management.anomalies_simulator import AnomaliesSimulator
from data_management.data_crawler import DataManager
import matplotlib.pyplot as plt
from common.data_frame_columns import TIMESTAMP, TEMPERATURE
from common.endpoints_urls import endpoints_config
import matplotlib.dates as mdates


def display_data_frame(df: pd.DataFrame, column_name: str, start_time=None, end_time=None):
    if start_time is None:
        start_time = df[TIMESTAMP].min()

    if end_time is None:
        end_time = df[TIMESTAMP].max()


    column_name_shortened = column_name.split('.')[-1]
    print(f"Plotting {column_name_shortened} for {df.name}")
    plt.figure(figsize=(10,8))

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
    plt.figure(figsize=(10,8))

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
    datas = DataManager().get_all_endpoints_data(endpoints_config, update=True)
    start_date_string = '01.04.2024 00:00'
    start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)

    end_date_string = '03.04.2024 23:59'
    end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)

    # display_data_frame(datas[0], TEMPERATURE, start_time, end_time)
    # display_data_frame(datas[2], PM10, start_time, end_time)

    # display_data_frame(datas[0], PRESSURE, start_time, end_time)
    destroyed_data = AnomaliesSimulator().extinction_parameter_in_range(datas[0], TEMPERATURE, start_time, end_time)
    # display_data_frame(destroyed_data, PRESSURE, start_time, end_time)

    display_data_frames([destroyed_data, datas[0]], TEMPERATURE, start_time, end_time)


if __name__ == '__main__':
    test()
    pass