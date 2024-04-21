# weather_rp5

This package provides functions for automatically retrieving weather records from the rp5.ru website.

## Installation

To install this project, run:
```
pip install weather_rp5
```

## Example Usage

To get records for the weather station in Sao Paulo starting on February 1, 2024 and ending on April 1, 2024,
you may use the following code (provided you have import pandas and date from the datetime module):
```
url = 'https://rp5.ru/Weather_archive_in_Sao_Paulo'
wmo_id = get_station_id(url)
start = date(2024, 2, 1)
end = date(2024, 4, 1)
df = get_weather_data(wmo_id, start, end, False)
```
If you need data from the airport (METAR) station, you may proceed as follows:
```
url = 'https://rp5.ru/Weather_archive_in_Sao_Paulo_(airport),_METAR'
station_id = get_station_id(url)
start = date(2024, 2, 1)
end = date(2024, 4, 1)
df = get_weather_data(station_id, start, end, True)
```

## Acknowledgement

The functions for sending post requests were taken from https://github.com/KonstantenKomkov/weather.
