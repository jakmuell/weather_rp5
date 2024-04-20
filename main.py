from datetime import date
from random import choice
from requests import Session
from requests.models import Response
from time import sleep

import rp5_ru_headers
import rp5_md_headers

browsers = ['Chrome', 'Firefox', 'Opera', 'Edge']

def get_phpsessid(items) -> str | None:
    phpsessid = None
    for x in items:
        if x[0] == 'PHPSESSID':
            phpsessid = x[1]
    return phpsessid

def prepare_weatherdownload(station_id, start_date: date,
                            last_date: date) -> None:
    """
    Funktioniert bisher nur für METAR Stationen, alle anderen später
    """

    url_base = "https://rp5.ru"
    current_session = Session()
    try:
        if not current_session.cookies.items():
            print("Performing get operation")
            current_session.get(url_base)
    except Exception as e:
        print(f"{url_base=}")
        print(f"Error in get: {e}")
    phpsessid = get_phpsessid(current_session.cookies.items())
    if phpsessid is None:
        current_session.close()
        current_session = Session()
        current_session.get(url_base)
        phpsessid = get_phpsessid(current_session.cookies.items())

    if url_base == 'https://rp5.ru' and phpsessid is not None:
        current_session.headers = rp5_ru_headers.get_header(phpsessid, choice(browsers))
    elif url_base == 'https://rp5.md' and phpsessid is not None:
        current_session.headers = rp5_md_headers.get_header(phpsessid, 'Chrome')
    elif phpsessid is not None:
        current_session.headers = rp5_ru_headers.get_header(phpsessid, choice(browsers))
    else:
        print("Error: phpsessid is None!")
    response: Response = None
    count = 5
    delay = 3
    while (response is None or response.text.find('http') == -1) and count > 0:
        print(f"Trying post with {url_base}/responses/reFileMetar.php")
        data={'metar': "4656", 'a_date1': start_date.strftime('%d.%m.%Y'),
                    'a_date2': last_date.strftime('%d.%m.%Y'), 'f_ed3': 4, 'f_ed4': 4, 'f_ed5': 20, 'f_pe': 1,
                    'f_pe1': 2, 'lng_id': 1, 'type': 'xls'}
        print(data)
        response: Response = current_session.post(
            f"{url_base}/responses/reFileMetar.php", data)
        print(response, response.text.find('http'))
        print(response.text)
        count -= 1
        sleep(delay)
        delay += 3

if __name__ == "__main__":
    station_id = "4656"  # Sao Paulo METAR
    start_date = date(2024,2,1)
    end_date = date(2024,2,10)
    prepare_weatherdownload(station_id, start_date, end_date)




