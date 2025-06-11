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

import httpx

from .utils import (get_phpsessid,
                    unpack_gz,
                    get_download_directory,
                    get_csv_path)
from .headers import get_header

BROWSERS = ['Chrome', 'Firefox', 'Opera', 'Edge']
URL_BASE = 'https://rp5.ru'


class FailedPostRequestError(Exception):
    """Raised when the weather data archive page shows an error message."""

    def __init__(self, message="Website returned 'error' when selecting weather data to archive"):
        super().__init__(message)



def prepare_weatherdownload(station_id, start_date: date, last_date: date,
                            is_metar: bool, encoding: Literal["ANSI", "UTF-8", "Unicode"]="UTF-8") -> str:
    """
    This function sends the Post request which is necessary in preparation
    for the actual download and returns the response of the post request
    which we can later use to retrieve the download url.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }

    with httpx.Client(headers=headers, timeout=10.0) as client:
        # Trigger session cookies
        try:
            client.get(f"{URL_BASE}/Weather_in_the_world")
        except httpx.HTTPError as e:
            print(f"Initial GET request failed: {e}")
            return ""

        phpsessid = get_phpsessid(client.cookies)

        if phpsessid is None:
            print("Failed to retrieve PHPSESSID cookie.")
            return ""

        # Set updated headers with session
        # client.headers.update(get_header(phpsessid, choice(BROWSERS)))
        headers_update = get_header(phpsessid, choice(BROWSERS))
        # Remove headers that can interfere
        headers_update.pop('Content-Length', None)
        headers_update.pop('Content-Type', None)
        client.headers.update(headers_update)

        # Map encoding to f_pe1
        encoding_map = {"ANSI": 1, "UTF-8": 2, "Unicode": 3}
        f_pe1 = encoding_map[encoding]

        # Build POST data
        data = {
            'a_date1': start_date.strftime('%d.%m.%Y'),
            'a_date2': last_date.strftime('%d.%m.%Y'),
            'f_ed3': 4,
            'f_ed4': 4,
            'f_ed5': 20,
            'f_pe': 1,
            'f_pe1': f_pe1,
            'lng_id': 1
        }

        if is_metar:
            data['metar'] = station_id
            url = f"{URL_BASE}/responses/reFileMetar.php"
            data['type'] = 'csv'
        else:
            data['wmo_id'] = station_id
            url = f"{URL_BASE}/responses/reFileSynop.php"
        
        data = {k: str(v) for k, v in data.items()}

        # Retry logic
        response = None
        attempts = 5
        delay = 3
        while attempts > 0:
            try:
                response = client.post(url, data=data)
                if "http" in response.text:
                    break
            except httpx.HTTPError as e:
                print(f"POST request failed (retrying): {e}")

            sleep(delay)
            delay += 3
            attempts -= 1

        if response is None or "http" not in response.text:
            print("Failed to retrieve valid download response.")
            return ""

        return response.text


def download_weather(station_id, start_date: date, last_date: date,
                     is_metar: bool) -> None:
    """
    This will download the weather data for a given station and time period
    as a csv file in the download directory of the computer.
    """
    download_dir = get_download_directory()
    if download_dir and os.path.isdir(download_dir):  # else use current working directory
        os.chdir(get_download_directory())
    response_text = prepare_weatherdownload(station_id, start_date, last_date,
                                            is_metar)
    if "error" in response_text.lower():
        raise FailedPostRequestError()
    url_start_idx = response_text.find('https')
    url_end_idx = response_text.find(' download')
    url = response_text[url_start_idx:url_end_idx]
    filename = get_csv_path(station_id, start_date, last_date)
    response = httpx.get(url, follow_redirects=True, timeout=20)
    if response.status_code != 200:
        logging.error("Cannot download file.")
        return None
    with open(f'{filename}.gz', 'wb') as file:
        file.write(response.content)
        logging.debug('File downloaded successfully.')
    unpack_gz(gz_file_path=f'{filename}.gz', destination_path=filename)
    return None
