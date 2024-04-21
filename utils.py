from datetime import date, timedelta
import os
import gzip
import shutil

def get_download_directory() -> str:
    if os.name == 'posix':  # macOS or Linux
        return os.path.expanduser('~/Downloads')
    elif os.name == 'nt':   # Windows
        return os.path.join(os.environ['HOMEPATH'], 'Downloads')
    return ''


def unpack_gz(gz_file_path, destination_path):
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


def get_csv_path(station_id, start: date, end: date) -> str:
    dir = get_download_directory()
    filename = (f'weather_{station_id}_{start.strftime("%Y%m%d")}_'
                f'{end.strftime("%Y%m%d")}.csv')
    return  os.path.join(dir, filename)


def extract_number(string):
    for i, char in enumerate(string):
        if not char.isdigit():
            return string[:i]
    return string


def split_time_period(start_date, end_date, num_intervals):
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
        print(start, end)

    return start_dates, end_dates
