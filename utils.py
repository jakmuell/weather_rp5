from datetime import date
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
