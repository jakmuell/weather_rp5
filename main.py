from datetime import date
import os

import pandas as pd

from downloader import download_weather
from cleanup import delete_comments_from_csv, format_dataframe
from utils import get_csv_path

def get_weather_data(
        station_id, start: date, end: date, is_metar: bool) -> pd.DataFrame:
    download_weather(station_id, start, end, is_metar)
    csv_path = get_csv_path(station_id, start, end)
    delete_comments_from_csv(csv_path, csv_path)
    df = format_dataframe(csv_path)
    os.remove(csv_path)
    return df


if __name__ == '__main__':

    # Test 1 (METAR)
    station_id = '4656'  # Sao Paulo METAR
    start_date = date(2024,2,1)
    end_date = date(2024,2,10)
    df = get_weather_data(station_id, start_date, end_date, True)
    print(df)

    # Test 2 (not METAR)
    wmo_id = 10384
    start_date = date(2024,2,1)
    end_date = date(2024,2,10)
    df = get_weather_data(wmo_id, start_date, end_date, False)
    print(df)




