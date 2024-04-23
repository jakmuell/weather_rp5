"""Collection of helper functions used in the other modules
that were moved here for readability.
"""

from datetime import date, timedelta
import os
import gzip
import shutil
from typing import List, Tuple

def get_download_directory() -> str:
    """Returns the path to the default download directory of the computer.
    """
    if os.name == 'posix':  # macOS or Linux
        return os.path.expanduser('~/Downloads')
    if os.name == 'nt':   # Windows
        return os.path.join(os.environ['HOMEPATH'], 'Downloads')
    return ''


def unpack_gz(gz_file_path: str, destination_path: str) -> None:
    """Unpacks a .gz file

    Args:
        gz_file_path (str): path to the .gz file
        destination_path (str): path where the unpacked file will be saved
    """
    with gzip.open(gz_file_path, 'rb') as f_in:
        with open(destination_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(gz_file_path)


def get_phpsessid(items):
    phpsessid = None
    for x in items:
        if x[0] == 'PHPSESSID':
            phpsessid = x[1]
    return phpsessid


def get_csv_path(station_id: int, start: date, end: date) -> str:
    """Returns the temporary download path for a weather data request

    Args:
        station_id (int): the integer code for the station by rp5.
        start (date): the first date of the request period.
        end (date): the last date of the request period.

    Returns:
        csv_path(str): The temporary download path 
    """
    download_dir = get_download_directory()
    filename = (f'weather_{station_id}_{start.strftime("%Y%m%d")}_'
                f'{end.strftime("%Y%m%d")}.csv')
    return  os.path.join(download_dir, filename)


def extract_number(string):
    for i, char in enumerate(string):
        if not char.isdigit():
            return string[:i]
    return string


def split_time_period(start_date: date, end_date: date,
                      num_intervals: int) -> Tuple[List[date], List[date]]:
    """Splits a time period into smaller time intervals.

    Args:
        start_date (date): The first date of the entire interval.
        end_date (date): The last date of the entire interval.
        num_intervals (int): The number of smaller intervals.

    Returns:
        A tuple. First element will be the list of starting points for the
        short intervals, second element will be the end points.
    """
    total_days = (end_date - start_date).days
    interval_days = total_days / num_intervals
    start_dates = []
    end_dates = []

    for i in range(num_intervals):
        start = start_date + timedelta(days=interval_days * i)
        start_dates.append(start)
        if i == num_intervals - 1:
            end = end_date
        else:
            end = start_date + timedelta(days=interval_days * (i + 1) - 1)
        end_dates.append(end)

    return start_dates, end_dates
