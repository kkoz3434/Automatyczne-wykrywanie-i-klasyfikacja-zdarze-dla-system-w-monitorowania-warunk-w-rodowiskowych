import pandas as pd

from common.data_frame_columns import PM1, PM10, PM2_5
from common.data_visualizer import display_data_frames
from common.endpoints_urls import endpoints_config
from data_management.anomalies_simulator import AnomaliesSimulator
from data_management.data_crawler import DataManager
from detectors.pseudo_periodic import PseudoPeriodicDetector

working_datetime_strings = [
    ['01.02.2023 00:00', '28.02.2023 23:59'],
    ['01.03.2023 00:00', '31.03.2023 23:59'],
    ['01.04.2023 00:00', '30.04.2023 23:59'],
    ['01.05.2023 00:00', '30.05.2023 23:59'],
    ['01.06.2023 00:00', '30.06.2023 23:59'],
]

working_datetime_strings_5_months = ['01.02.2022 00:00', '30.06.2023 23:59']
test_date_time_strings = ['01.03.2024 00:00', '30.03.2024 23:59']

def test():
    datas = DataManager(True).get_all_endpoints_data(endpoints_config, update=False)

    # for config in working_datetime_strings:
    #     start_date_string = config[0]
    #     start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)
    #     end_date_string = config[1]
    #     end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)
    #     column = PM10
    #     display_data_frames(datas, column, start_time, end_time)

    start_date_string = test_date_time_strings[0]
    start_time = pd.to_datetime(start_date_string, format='%d.%m.%Y %H:%M', utc=True)
    end_date_string = test_date_time_strings[1]
    end_time = pd.to_datetime(end_date_string, format='%d.%m.%Y %H:%M', utc=True)
    column = PM10
    display_data_frames(datas, column, start_time, end_time)

if __name__ == '__main__':
    test()