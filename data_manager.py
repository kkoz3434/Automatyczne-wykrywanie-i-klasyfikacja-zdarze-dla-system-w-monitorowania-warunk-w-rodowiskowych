import time

import pandas as pd
import requests
from datetime import datetime, timezone

TIMESTAMP = 'timestamp'
CSV_PREFIX = './results/'
CSV_SUFFIX = '.csv'

config = {
    "stationList": [
        {"name": "Gronie", "url": "https://datahub.ki.agh.edu.pl/api/endpoints/70/data/"},
        {"name": "Urząd Gminy", "url": "https://datahub.ki.agh.edu.pl/api/endpoints/71/data/"},
        {"name": "Młynne", "url": "https://datahub.ki.agh.edu.pl/api/endpoints/72/data/"},
        {"name": "Sucharskiego", "url": "https://datahub.ki.agh.edu.pl/api/endpoints/73/data/"},
        {"name": "Twardowskiego", "url": "https://datahub.ki.agh.edu.pl/api/endpoints/74/data/"},
        {"name": "Konopnickiej", "url": "https://datahub.ki.agh.edu.pl/api/endpoints/75/data/"}
    ],
}


def makeRequests(station, url, offset=None, limit=None, columns_to_save=None):
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


def createDataFrame(station, time_from, time_end, columns_to_save=None):
    df = None
    url = station['url']
    time_from_comp = pd.to_datetime(time_from, utc=True)
    time_end_comp = pd.to_datetime(time_end, utc=True)

    if time_from_comp >= time_end_comp:
        return f"Invalid datetime: {time_from_comp} is later than {time_end_comp}"

    counter = 0
    while True:
        counter += 1
        entries, nextUrl = makeRequests(station, url, limit=100)
        if entries is not None and nextUrl is not None and len(entries) > 0:
            df_list = [pd.json_normalize(entry) for entry in entries]
            new_measurements = pd.concat(df_list, ignore_index=True)
            new_measurements[TIMESTAMP] = pd.to_datetime(new_measurements[TIMESTAMP], utc=True) + pd.Timedelta(hours=1)
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


def getTodaysDateString():
    today_utc = datetime.utcnow()
    end_of_day_utc = today_utc.replace(hour=23, minute=59, second=59)
    utc_offset = timezone.utc.utcoffset(today_utc)
    formatted_date_string = end_of_day_utc.replace(tzinfo=timezone(utc_offset)).strftime('%Y-%m-%d %H:%M:%S') + "+00:00"
    return formatted_date_string


def getMinimumDateString():
    today_utc = datetime.min
    end_of_day_utc = today_utc.replace(hour=23, minute=59, second=59)
    utc_offset = timezone.utc.utcoffset(today_utc)
    formatted_date_string = end_of_day_utc.replace(tzinfo=timezone(utc_offset)).strftime('%Y-%m-%d %H:%M:%S') + "+00:00"
    return formatted_date_string


def getNewestDate(dataframe):
    if dataframe.empty:
        return None
    return dataframe[TIMESTAMP].max()


def getStationCSVFileName(station):
    return CSV_PREFIX + station['name'] + CSV_SUFFIX


def getDataFromCSV(filename):
    try:
        df = pd.read_csv(filename)
        df[TIMESTAMP] = pd.to_datetime(df[TIMESTAMP], utc=True)
        return df
    except FileNotFoundError:
        print(f"File not found: {filename}")
        print(f"Creating new dataframe")
        return None


def updateCSV(station, old_df):
    newest_date = getNewestDate(old_df)
    updated = createDataFrame(station, newest_date, getTodaysDateString())
    if isinstance(updated, pd.core.frame.DataFrame):
        merged_df = pd.concat([old_df, updated], ignore_index=True)
        merged_df.to_csv(getStationCSVFileName(station), index=False)
        return merged_df
    return old_df


def getAllEndpointsData(config, update=False):
    stationList = config["stationList"]
    results = []

    for station in stationList:
        print("Loading station data: " + station['name'] + "  " + station['url'])

        df = getDataFromCSV(getStationCSVFileName(station))
        if df is not None:
            if update:
                print(f"    # Minimal data: {df[TIMESTAMP].min()}")
                print(f"    # Maximal data: {df[TIMESTAMP].max()}")

                print("# Updating data for given endpoint... ")
                df = updateCSV(station, df)
        else:
            df = createDataFrame(station, getMinimumDateString(), getTodaysDateString())
            df.to_csv(getStationCSVFileName(station), index=False)
        print(f"    # Minimal data: {df[TIMESTAMP].min()}")
        print(f"    # Maximal data: {df[TIMESTAMP].max()}")
        results.append(df)

    return results


if __name__ == '__main__':
    datas = getAllEndpointsData(config, update=True)
