from datetime import date
from random import choice
from requests import Session
from requests.models import Response
from time import sleep

import rp5_ru_headers
import rp5_md_headers

BROWSERS = ['Chrome', 'Firefox', 'Opera', 'Edge']
URL_BASE = 'https://rp5.ru'

def get_phpsessid(items):
    phpsessid = None
    for x in items:
        if x[0] == 'PHPSESSID':
            phpsessid = x[1]
    return phpsessid

def prepare_weatherdownload(station_id, start_date: date,
                            last_date: date,
                            is_metar: bool) -> None:
    current_session = Session()
    try:
        if not current_session.cookies.items():
            print('Performing get operation')
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
        current_session.headers = rp5_ru_headers.get_header(phpsessid, choice(BROWSERS))
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
            print(data)
            response = current_session.post(
                f'{URL_BASE}/responses/reFileSynop.php', data
            )
        print(response, response.text.find('http'))
        print(response.text)
        count -= 1
        sleep(delay)
        delay += 3

if __name__ == '__main__':

    # Test 1 (METAR)
    station_id = '4656'  # Sao Paulo METAR
    start_date = date(2024,2,1)
    end_date = date(2024,2,10)
    prepare_weatherdownload(station_id, start_date, end_date, True)

    # Test 2 (not METAR)
    wmo_id = 83781
    start_date = date(2024,2,1)
    end_date = date(2024,2,10)
    prepare_weatherdownload(wmo_id, start_date, end_date, False)




