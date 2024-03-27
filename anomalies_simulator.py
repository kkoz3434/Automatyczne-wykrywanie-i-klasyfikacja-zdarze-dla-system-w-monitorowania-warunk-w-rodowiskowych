import pandas as pd
from datetime import datetime, timezone
from data_manager import DataManager

from data_frame_columns import TIMESTAMP, PRESSURE
from endpoints_urls import endpoints_config


class AnomaliesSimulator:

    def zerosInRange(self, df: pd.DataFrame, column_name: str, start_time, end_time, value=0) -> pd.DataFrame:
        selected_data = df.copy()
        selected_data = selected_data[
            (selected_data[TIMESTAMP] >= start_time) & (selected_data[TIMESTAMP] <= end_time)].copy()
        selected_data.loc[:, column_name] = value
        modified_data = df.copy()
        modified_data.update(selected_data)

        return modified_data


def tests():
    datas = DataManager().get_all_endpoints_data(endpoints_config, update=False)
    date_string = '21.03.2024 13:00'

    start_time = pd.to_datetime(date_string, format='%d.%m.%Y %H:%M', utc=True)
    modified = AnomaliesSimulator().zerosInRange(datas[0], PRESSURE, start_time,
                                                 pd.to_datetime(datetime.now(), utc=True),55)
    print(modified.loc[modified[TIMESTAMP] > start_time, PRESSURE])


if __name__ == '__main__':
    tests()
