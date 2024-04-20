from datetime import date
import os
from random import choice
from requests import Session
import requests
from requests.models import Response
from time import sleep

from utils import get_download_directory, unpack_gz



if __name__ == '__main__':

    # Test 1 (METAR)
    station_id = '4656'  # Sao Paulo METAR
    start_date = date(2024,2,1)
    end_date = date(2024,2,10)
    download_weather(station_id, start_date, end_date, True)
    # prepare_weatherdownload(station_id, start_date, end_date, True)

    # Test 2 (not METAR)
    wmo_id = 10384
    start_date = date(2024,2,1)
    end_date = date(2024,2,10)
    download_weather(wmo_id, start_date, end_date, False)
    # prepare_weatherdownload(wmo_id, start_date, end_date, False)




