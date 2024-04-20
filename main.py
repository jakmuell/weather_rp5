from datetime import date
from random import choice
import os
import shutil
import gzip
from requests import Session
import requests
from requests.models import Response
from time import sleep

import headers

BROWSERS = ['Chrome', 'Firefox', 'Opera', 'Edge']
URL_BASE = 'https://rp5.ru'

def get_phpsessid(items):
    phpsessid = None
    for x in items:
        if x[0] == 'PHPSESSID':
            phpsessid = x[1]
    return phpsessid


def unpack_gz(gz_file_path, destination_path):
    with gzip.open(gz_file_path, 'rb') as f_in:
        with open(destination_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(gz_file_path)
    
    
def prepare_weatherdownload(station_id, start_date: date,
                            last_date: date,
                            is_metar: bool) -> str:
    current_session = Session()
    try:
        if not current_session.cookies.items():
            current_session.get(URL_BASE)
    except Exception as e:
        print(f'{URL_BASE=}')
        print(f'Error in get: {e}')
    phpsessid = get_phpsessid(current_session.cookies.items())
    if phpsessid is None:
        current_session.close()
        current_session = Session()
        current_session.get(URL_BASE)
        phpsessid = get_phpsessid(current_session.cookies.items())

    if phpsessid is not None:
        current_session.headers = headers.get_header(phpsessid, choice(BROWSERS))
    else:
        print('Error: phpsessid is None!')

    response: Response = None
    count = 5
    delay = 3
    while (response is None or response.text.find('http') == -1) and count > 0:
        if is_metar:
            data={
                'metar': station_id,
                'a_date1': start_date.strftime('%d.%m.%Y'),
                'a_date2': last_date.strftime('%d.%m.%Y'),
                'f_ed3': 4,
                'f_ed4': 4,
                'f_ed5': 20,
                'f_pe': 1,
                'f_pe1': 2,
                'lng_id': 1,
                'type': 'csv'
            }
            response = current_session.post(
                f'{URL_BASE}/responses/reFileMetar.php', data
            )
        else:
            data = {
                'wmo_id': station_id,
                'a_date1': start_date.strftime('%d.%m.%Y'),
                'a_date2': last_date.strftime('%d.%m.%Y'),
                'f_ed3': 4,
                'f_ed4': 4,
                'f_ed5': 20,
                'f_pe': 1,
                'f_pe1': 2,
                'lng_id': 1
            }
            response = current_session.post(
                f'{URL_BASE}/responses/reFileSynop.php', data
            )
        count -= 1
        sleep(delay)
        delay += 3
    return response.text

def download_weather(station_id, start_date: date,
                     last_date: date, is_metar: bool) -> None:
    response_text = prepare_weatherdownload(station_id, start_date,
                                            last_date, is_metar)
    url_start_idx = response_text.find('https')
    url_end_idx = response_text.find(' download')
    url = response_text[url_start_idx:url_end_idx]
    print(url)
    filename = (f'weather_{station_id}_{start_date.strftime("%Y%m%d")}_'
                f'{last_date.strftime("%Y%m%d")}.csv')
    response = requests.get(url, allow_redirects=True)
    if response.status_code != 200:
        print("Cannot download file.")
        return None
    with open(f'{filename}.gz', 'wb') as file:
        file.write(response.content)
        print('File downloaded successfully.')
    unpack_gz(gz_file_path=f'{filename}.gz', destination_path=filename)

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




