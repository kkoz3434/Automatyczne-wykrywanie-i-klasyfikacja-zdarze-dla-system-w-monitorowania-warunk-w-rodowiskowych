import numpy as np

import pandas as pd

from data_management.anomalies_simulator import AnomaliesSimulator
from common.data_frame_columns import TIMESTAMP, PM1
from data_management.data_crawler import DataManager
from common.data_visualizer import display_data_frames
from common.endpoints_urls import endpoints_config


class PseudoPeriodicDetector():
    def detect_by_periodic_avg(self, df: pd.DataFrame, column, start_time, end_time,
                               time_step_in_hours=1, max_depth_in_days=5, threshold=2):
        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] < end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)

        begin = start_time
        end = start_time + pd.Timedelta(hours=time_step_in_hours)

        detected_list = []
        while begin < end_time:
            # check range
            if end > end_time:
                end = end_time

            # prepare previous values
            previous_column_values = []
            for i in range(0, max_depth_in_days):
                prev_start = begin - pd.Timedelta(days=i)
                prev_end = end - pd.Timedelta(days=i)
                prev_filtered = df[
                    (df[TIMESTAMP] >= prev_start) & (df[TIMESTAMP] < prev_end)]
                previous_column_values.extend(prev_filtered[column])

            if len(previous_column_values) > 0:
                # calculate needed params
                average = np.mean(np.array(previous_column_values))
                std = np.std(previous_column_values)
                if std == 0.0:
                    return df

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
        if len(detected_list) > 0:
            outliers = pd.concat(detected_list)
            outliers.name = df.name + "_pseudo_periodic_avg"
            return outliers
        else:
            return df

    def detect_by_periodic_mad(self, df: pd.DataFrame, column, start_time, end_time,
                               time_step_in_hours=1, max_depth_in_days=5, threshold=2):
        filtered_df = df[(df[TIMESTAMP] >= start_time) & (df[TIMESTAMP] < end_time)]
        filtered_df = filtered_df.sort_values(by=TIMESTAMP)

        begin = start_time
        end = start_time + pd.Timedelta(hours=time_step_in_hours)

        detected_list = []
        while begin < end_time:
            # check range
            if end > end_time:
                end = end_time

            # prepare previous values
            previous_column_values = []
            for i in range(0, max_depth_in_days):
                prev_start = begin - pd.Timedelta(days=i)
                prev_end = end - pd.Timedelta(days=i)
                prev_filtered = df[
                    (df[TIMESTAMP] >= prev_start) & (df[TIMESTAMP] < prev_end)]
                previous_column_values.extend(prev_filtered[column])

            if len(previous_column_values) > 0:
                # calculate needed params
                median = np.median(previous_column_values)
                mad = 1.486 * np.median(np.abs(previous_column_values - median))
                if mad == 0:
                    mad = 1.253314 * np.mean(previous_column_values)
                    if mad == 0.0:
                        return df

                # filter sensor data and prepare mask
                filtered = filtered_df[(filtered_df[TIMESTAMP] >= begin) & (filtered_df[TIMESTAMP] < end)]
                values = np.array(filtered[column])

                z_scored = ((values - median) / mad)
                mask = np.abs(z_scored) > threshold

                # apply mask
                detected = filtered[mask]
                detected_list.append(detected)

            begin = end
            end += pd.Timedelta(hours=time_step_in_hours)
        if len(detected_list) > 0:
            outliers = pd.concat(detected_list)
            outliers.name = df.name + "_pseudo_periodic_mad"
            return outliers
        else:
            return df

    def detect_by_periodic_avg_network_level(self, datas: list[pd.DataFrame], df: pd.DataFrame, column, start_time,
                                             end_time,
                                             time_step_in_hours=1, max_depth_in_days=5, threshold=2):
        # prepare network related_data
        max_depth_time = start_time - pd.Timedelta(days=max_depth_in_days)
        filtered_datas = []

        for data in datas:
            filtered = data[(data[TIMESTAMP] >= max_depth_time) & (data[TIMESTAMP] < end_time)]
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
            for i in range(0, max_depth_in_days):
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

        if len(detected_list) > 0:
            outliers = pd.concat(detected_list)
            outliers.name = df.name + "_pseudo_periodic_avg_network"
            return outliers
        else:
            return df

    def detect_by_periodic_mad_network_level(self, datas: list[pd.DataFrame], df: pd.DataFrame, column, start_time,
                                             end_time,
                                             time_step_in_hours=1, max_depth_in_days=5, threshold=2):

        max_depth_time = start_time - pd.Timedelta(days=max_depth_in_days)
        filtered_datas = []

        for data in datas:
            filtered = data[(data[TIMESTAMP] >= max_depth_time) & (data[TIMESTAMP] <= end_time)]
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
            for i in range(0, max_depth_in_days):
                network_start = begin - pd.Timedelta(days=i)
                network_end = end - pd.Timedelta(days=i)
                network_filtered = network_data[
                    (network_data[TIMESTAMP] >= network_start) & (network_data[TIMESTAMP] < network_end)]
                network_column_values.extend(network_filtered[column])

            if len(network_column_values) > 0:
                # calculate needed params
                median = np.median(network_column_values)
                mad = 1.486 * np.median(np.abs(network_column_values - median))
                if mad == 0:
                    mad = 1.253314 * np.mean(network_column_values)

                # filter sensor data and prepare mask
                filtered = filtered_df[(filtered_df[TIMESTAMP] >= begin) & (filtered_df[TIMESTAMP] < end)]
                values = np.array(filtered[column])

                z_scored = ((values - median) / mad)
                mask = np.abs(z_scored) > threshold

                # apply mask
                detected = filtered[mask]
                detected_list.append(detected)

            begin = end
            end += pd.Timedelta(hours=time_step_in_hours)

        if len(detected_list) > 0:
            outliers = pd.concat(detected_list)
            outliers.name = df.name + "_pseudo_periodic_mad_network"
            return outliers
        else:
            return df


def test():
    datas = DataManager(True).get_all_endpoints_data(endpoints_config, update=False)

    start_date_string = '17.04.2024 00:00'
    start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)

    end_date_string = '17.04.2024 23:59'
    end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)

    column = PM1
    display_data_frames(datas, column, start_time, end_time)

    destroyed = AnomaliesSimulator().zero_random_in_range(datas[1], column, start_time, end_time, 15)

    outliers = PseudoPeriodicDetector().detect_by_periodic_avg_network_level(datas[2:], datas[0], column, start_time,
                                                                             end_time,
                                                                             threshold=3,
                                                                             max_depth_in_days=1)

    display_data_frames([destroyed, outliers], column, start_time, end_time)


if __name__ == '__main__':
    test()
