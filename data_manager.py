import time

import pandas as pd
import requests
from datetime import datetime, timezone

from data_frame_columns import TIMESTAMP
from date_time_helper import get_minimum_date_string, get_today_date_string
from endpoints_urls import endpoints_config

CSV_PREFIX = './results/'
CSV_SUFFIX = '.csv'


class DataManager:
    def make_requests(self, station, url, offset=None, limit=None, columns_to_save=None):
        params = {}
        if offset is not None:
            params['offset'] = offset

        if limit is not None:
            params['limit'] = limit

        counter = 1
        response = requests.get(url, params=params)
        while response.status_code != 200:
            print(f"    ## Error getting data: {response.status_code}, waiting for try no: {counter} ##")
            response = requests.get(url, params=params)
            counter += 1
            time.sleep(1)

        json_data = response.json()
        entries = json_data['results']
        next = None
        try:
            next = json_data['next']
        except KeyError:
            print("Error parsing {next} value for station: " + station['name'])

        return entries, next

    def create_data_frame(self, station, time_from, time_end, columns_to_save=None):
        df = None
        url = station['url']
        time_from_comp = pd.to_datetime(time_from, utc=True)
        time_end_comp = pd.to_datetime(time_end, utc=True)

        if time_from_comp >= time_end_comp:
            return f"Invalid datetime: {time_from_comp} is later than {time_end_comp}"

        counter = 0
        while True:
            counter += 1
            entries, nextUrl = self.make_requests(station, url, limit=100)
            if entries is not None and nextUrl is not None and len(entries) > 0:
                df_list = [pd.json_normalize(entry) for entry in entries]
                new_measurements = pd.concat(df_list, ignore_index=True)
                new_measurements[TIMESTAMP] = pd.to_datetime(new_measurements[TIMESTAMP], utc=True) + pd.Timedelta(
                    hours=1)
                if counter % 20 == 0:
                    print(f"    Crawling url: {url.split('?')[1]} DateTime: {new_measurements[TIMESTAMP].min()}")
                if df is None:
                    df = new_measurements
                else:
                    if (len(new_measurements) > 0):
                        df = pd.concat([df, new_measurements], ignore_index=True)

                value_exists = (new_measurements[TIMESTAMP] < time_from)
                if any(value_exists):
                    filtered_df = df[(df[TIMESTAMP] > time_from) & (df[TIMESTAMP] <= time_end)]
                    if columns_to_save is not None:
                        filtered_df = filtered_df[columns_to_save]
                    return filtered_df
                else:
                    url = nextUrl
            else:
                return df

    def get_newest_date(self, dataframe):
        if dataframe.empty:
            return None
        return dataframe[TIMESTAMP].max()

    def get_station_csv_file_name(self, station):
        return CSV_PREFIX + station['name'] + CSV_SUFFIX

    def get_data_from_csv(self, station):
        filename = self.get_station_csv_file_name(station)
        try:
            df = pd.read_csv(filename)
            df[TIMESTAMP] = pd.to_datetime(df[TIMESTAMP], utc=True)
            return df
        except FileNotFoundError:
            print(f"File not found: {filename}")
            print(f"Creating new dataframe")
            return None

    def update_csv(self, station, old_df):
        newest_date = self.get_newest_date(old_df)
        updated = self.create_data_frame(station, newest_date, get_today_date_string())
        if isinstance(updated, pd.core.frame.DataFrame):
            merged_df = pd.concat([old_df, updated], ignore_index=True)
            merged_df.to_csv(self.get_station_csv_file_name(station))
            return merged_df
        return old_df

    def get_all_endpoints_data(self, config, update=False):
        stationList = config["stationList"]
        results = []

        for station in stationList:
            print("Loading station data: " + station['name'] + "  " + station['url'])

            df = self.get_data_from_csv(station)
            if df is not None:
                if update:
                    print(f"    # Minimal data: {df[TIMESTAMP].min()}")
                    print(f"    # Maximal data: {df[TIMESTAMP].max()}")

                    print("# Updating data for given endpoint... ")
                    df = self.update_csv(station, df)
            else:
                df = self.create_data_frame(station, get_minimum_date_string(), get_today_date_string())
                df.to_csv(self.get_station_csv_file_name(station))
            print(f"    # Minimal data: {df[TIMESTAMP].min()}")
            print(f"    # Maximal data: {df[TIMESTAMP].max()}")
            results.append(df)

        return results
