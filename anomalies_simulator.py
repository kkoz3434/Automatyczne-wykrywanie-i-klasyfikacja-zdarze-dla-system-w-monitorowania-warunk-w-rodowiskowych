import pandas as pd
from datetime import datetime, timezone
from data_manager import DataManager

from data_frame_columns import TIMESTAMP, PRESSURE
from endpoints_urls import endpoints_config


class AnomaliesSimulator:

    def zeros_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, value=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data.loc[:, column_name] = value
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data

    def scaled_in_range(self, df: pd.DataFrame, column_name: str, start_time, end_time, scalar=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data[column_name] *= scalar
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data


def tests():
    datas = DataManager().get_all_endpoints_data(endpoints_config, update=True)
    date_string = '21.03.2024 13:00'

    start_time = pd.to_datetime(date_string, format='%d.%m.%Y %H:%M', utc=True)
    print(datas[0].loc[datas[0][TIMESTAMP] > start_time, PRESSURE])
    modified = AnomaliesSimulator().scaled_in_range(datas[0], PRESSURE, start_time,
                                                    pd.to_datetime(datetime.now(), utc=True), 1000)
    print(modified.loc[modified[TIMESTAMP] > start_time, PRESSURE])


if __name__ == '__main__':
    tests()
