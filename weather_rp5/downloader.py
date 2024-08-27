"""
This module contains the functions for sending post requests to rp5 and for
downloading the zip folder of weather data from the site
"""
from datetime import date
import logging
import os
from random import choice
from time import sleep
from typing import Literal

import requests
from requests.models import Response

from .utils import (get_phpsessid,
                    unpack_gz,
                    get_download_directory,
                    get_csv_path)
from .headers import get_header

BROWSERS = ['Chrome', 'Firefox', 'Opera', 'Edge']
URL_BASE = 'https://rp5.ru'


def prepare_weatherdownload(station_id, start_date: date, last_date: date,
                            is_metar: bool, encoding: Literal["ANSI", "UTF-8", "Unicode"]="UTF-8") -> str:
    """
    This function sends the Post request which is necessary in preparation
    for the actual download and returns the response of the post request
    which we can later use to retrieve the download url.
    """
    current_session = requests.Session()
    try:
        if not current_session.cookies.items():
            current_session.get(URL_BASE)
    except Exception as e:
        print(f'{URL_BASE=}')
        print(f'Error in get: {e}')
    phpsessid = get_phpsessid(current_session.cookies.items())
    if phpsessid is None:
        current_session.close()
        current_session = requests.Session()
        current_session.get(URL_BASE)
        phpsessid = get_phpsessid(current_session.cookies.items())

    if phpsessid is not None:
        current_session.headers = get_header(phpsessid, choice(BROWSERS))
    else:
        print('Error: phpsessid is None!')

    response: Response = None
    count = 5
    delay = 3
    match encoding:
        case "ANSI": f_pe1 = 1
        case "UTF-8": f_pe1 = 2
        case "Unicode": f_pe1 = 3
    while (response is None or response.text.find('http') == -1) and count > 0:
        if is_metar:
            data = {
                'metar': station_id,
                'a_date1': start_date.strftime('%d.%m.%Y'),
                'a_date2': last_date.strftime('%d.%m.%Y'),
                'f_ed3': 4,
                'f_ed4': 4,
                'f_ed5': 20,
                'f_pe': 1,
                'f_pe1': f_pe1,
                'lng_id': 1,
                'type': 'csv'
            }
            response = current_session.post(
                f'{URL_BASE}/responses/reFileMetar.php', data)
        else:
            data = {
                'wmo_id': station_id,
                'a_date1': start_date.strftime('%d.%m.%Y'),
                'a_date2': last_date.strftime('%d.%m.%Y'),
                'f_ed3': 4,
                'f_ed4': 4,
                'f_ed5': 20,
                'f_pe': 1,
                'f_pe1': f_pe1,
                'lng_id': 1
            }
            response = current_session.post(
                f'{URL_BASE}/responses/reFileSynop.php', data)
        count -= 1
        sleep(delay)
        delay += 3
    return response.text


def download_weather(station_id, start_date: date, last_date: date,
                     is_metar: bool) -> None:
    """
    This will download the weather data for a given station and time period
    as a csv file in the download directory of the computer.
    """
    os.chdir(get_download_directory())
    response_text = prepare_weatherdownload(station_id, start_date, last_date,
                                            is_metar)
    url_start_idx = response_text.find('https')
    url_end_idx = response_text.find(' download')
    url = response_text[url_start_idx:url_end_idx]
    filename = get_csv_path(station_id, start_date, last_date)
    response = requests.get(url, allow_redirects=True, timeout=20)
    if response.status_code != 200:
        logging.error("Cannot download file.")
        return None
    with open(f'{filename}.gz', 'wb') as file:
        file.write(response.content)
        logging.debug('File downloaded successfully.')
    unpack_gz(gz_file_path=f'{filename}.gz', destination_path=filename)
    return None
