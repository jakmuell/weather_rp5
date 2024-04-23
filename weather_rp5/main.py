from datetime import date, datetime
from math import ceil
import os
import requests

from bs4 import BeautifulSoup
import pandas as pd

from .downloader import download_weather
from .cleanup import delete_comments_from_csv, format_dataframe
from .utils import get_csv_path, extract_number, split_time_period


def get_station_id(rp5_link: str) -> int:
    """Retrieves the weather station id needed for the download.
    For non-airport stations this is the number that can be seen on the site
    under 'weather station number'.
    For airport stations (METAR) this is different from the weather station
    number.

    Args:
        rp5_link (str): the rp5 link, e.g.
        'https://rp5.ru/Weather_archive_in_Sao_Paulo'

    Returns:
        station_id(int): The integer code used by rp5 for identifying
        weather stations
    """
    response = requests.get(rp5_link, timeout=5)
    text = response.text
    if 'METAR' in rp5_link:
        pos = text.find('fFileMetarGet')
        substring = text[(pos+16):]
        return int(extract_number(substring))
    soup = BeautifulSoup(response.text, 'html.parser')
    input_element = soup.find('input', id='wmo_id')
    return int(input_element['value'])


def _get_weather_data_for_short_range(
        station_id: int, start: date, end: date,
        is_metar: bool) -> pd.DataFrame:
    if (end-start).days > 180:
        raise ValueError('For time ranges longer than 180 days use '
                         'get_weather_data function instead')
    download_weather(station_id, start, end, is_metar)
    csv_path = get_csv_path(station_id, start, end)
    delete_comments_from_csv(csv_path, csv_path)
    df = format_dataframe(csv_path)
    os.remove(csv_path)
    return df
    

def get_weather_data(
        station_id: int, start: date, end: date,
        is_metar: bool) -> pd.DataFrame:
    """Function that retrieves weather data for a specific station from
    the rp5 website and saves it into a pandas dataframe.

    Args:
        station_id (int): the number given by rp5 to identify the weather
        station. If you do not know the id, you can use the get_station_id
        function to find it.
        start (date): the first date for which to get the data
        end (date): the last date for which to get the data
        is_metar (bool): pass True if the station_id belongs to an airport
        (METAR) station, else False.

    Returns:
        weather_data (pd.DataFrame): dataframe with the weather records
        according to the parameters provided.
    """
    today: date = datetime.now().date()
    end = min(end, today)
    if end < start:
        raise ValueError('End date must be after start date.')
    total_days = (end-start).days
    if total_days <= 180:
        return _get_weather_data_for_short_range(
            station_id, start, end, is_metar)
    num_partial_downloads = ceil(total_days/180)
    start_dates, end_dates = split_time_period(
        start, end, num_intervals=num_partial_downloads)
    df = pd.DataFrame()
    for start_partial, end_partial in zip(start_dates, end_dates):
        df_partial = _get_weather_data_for_short_range(
            station_id, start=start_partial, end=end_partial, is_metar=is_metar
        )
        df = pd.concat([df, df_partial], axis='index').reset_index(drop=True)
    return df


if __name__ == '__main__':

    # Test 1 (METAR)
    station_id = get_station_id(
        'https://rp5.ru/Weather_archive_in_Sao_Paulo_(airport),_METAR')
    # station_id = 4656
    start_date = date(2023,2,1)
    end_date = date(2024,2,10)
    df = get_weather_data(station_id, start_date, end_date, True)
    print(df)

    # Test 2 (not METAR)
    wmo_id = get_station_id(
        'https://rp5.ru/Weather_archive_in_Sao_Paulo'
    )
    # wmo_id = 10384
    start_date = date(2024,2,1)
    end_date = date(2024,2,10)
    df = get_weather_data(wmo_id, start_date, end_date, False)
    print(df)

