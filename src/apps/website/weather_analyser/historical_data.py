import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

class HistoricalData:
    def __init__(self, latitude, longitude, start="2015-01-01", end="2024-01-01"):
        start_date_str = start
        end_date_str = end

        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "rain_sum"]
        }
        responses = openmeteo.weather_api(url, params=params)

        response = responses[0]
        daily = response.Daily()
        self.daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        self.daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        self.daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
        self.daily_rain_sum = daily.Variables(3).ValuesAsNumpy()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            )
        }
        daily_data["temperature_2m_max"] = self.daily_temperature_2m_max
        daily_data["temperature_2m_min"] = self.daily_temperature_2m_min
        daily_data["precipitation_sum"] = self.daily_precipitation_sum
        daily_data["rain_sum"] = self.daily_rain_sum

        self.daily_dataframe = pd.DataFrame(data=daily_data)
