import json

import pandas as pd
from django.http import JsonResponse
from django.views.generic import TemplateView
from src.apps.website.weather_analyser.forcast_data import ForecastData
from src.apps.website.weather_analyser.historical_data import HistoricalData
from datetime import datetime, timedelta
from src.apps.website.weather_analyser.predictions import  make_predictions
import numpy as np
def _round(value):
    return round(float(value), 2)


class HomePageView(TemplateView):
    template_name = "website/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class EagleCreekPageView(TemplateView):
    template_name = "eaglecreek.html"

class CreekPageView(TemplateView):

    def get_template_names(self):
        return [f"creek.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        creekname = self.kwargs.get('creekname')
        context['creekname'] = creekname
        return context





def get_season(date):

    if (date.month == 12 and date.day >= 20) or (date.month in [1, 2]) or (date.month == 3 and date.day < 20):
        return 'Winter'
    elif (date.month == 3 and date.day >= 20) or (date.month in [4, 5]) or (date.month == 6 and date.day < 20):
        return 'Spring'
    elif (date.month == 6 and date.day >= 20) or (date.month in [7, 8]) or (date.month == 9 and date.day < 20):
        return 'Summer'
    elif (date.month == 9 and date.day >= 20) or (date.month in [10, 11]) or (date.month == 12 and date.day < 20):
        return 'Fall'
    else:
        return 'Winter'

def predictions(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    creek = request.GET.get('creek')

    if lat and lon:
        forecast_data = ForecastData(latitude=lat, longitude=lon, forecast_days=7)
        metrics = []

        for i in range(7):
            today = datetime.now() + timedelta(days=i)
            today_str = today.strftime('%Y-%m-%d')
            today_data = forecast_data.daily_dataframe[forecast_data.daily_dataframe['date'] == today_str]

            if today_data.empty:
                continue
            temp_max = today_data['temperature_2m_max'].values[0]
            temp_min = today_data['temperature_2m_min'].values[0]
            today_temp_avg = float((temp_max + temp_min) / 2)
            today_precipitation = float(today_data['precipitation_sum'].values[0])
            rainfall = float(today_data['rain_sum'].values[0])

            season = get_season(today)

            metrics.append({
                "date": today_str,
                "Precipitation":_round(today_precipitation),
                "Temp": _round(today_temp_avg),
                "MaxTemp": _round(temp_max),
                "MinTemp": _round(temp_min),
                "Season": season,
                "Rainfall":rainfall
            })

        dates = [entry['date'] for entry in metrics]
        precipitation = [entry['Precipitation'] for entry in metrics]
        temp = [entry['Temp'] for entry in metrics]
        maxTemp = [entry['MaxTemp'] for entry in metrics]
        minTemp = [entry['MinTemp'] for entry in metrics]
        season = [entry['Season'] for entry in metrics]
        rainfall = [entry['Rainfall'] for entry in metrics]


        df = pd.DataFrame({
            "date": dates,
            "Precipitation": precipitation,
            "Temp": temp,
            "MaxTemp": maxTemp,
            "MinTemp": minTemp,
            "Season": season,
        })

        # Generate predictions based on the dataframe
        predictions = make_predictions(creek, df)

        # Combine metrics and predictions
        for i, prediction in enumerate(predictions):
            metrics[i]['prediction'] =int(prediction)

        return JsonResponse(metrics, safe=False)


def historical_predictions(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    creek = request.GET.get('creek')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    metrics = []

    if lat and lon and start_date and end_date:
        historical_data = HistoricalData(latitude=lat, longitude=lon, start=start_date, end=end_date)

        # Fetch historical data
        df = historical_data.daily_dataframe

        # Preprocessing data: convert to numeric and remove rows with missing data
        df['temperature_2m_max'] = pd.to_numeric(df['temperature_2m_max'], errors='coerce')
        df['temperature_2m_min'] = pd.to_numeric(df['temperature_2m_min'], errors='coerce')
        df['precipitation_sum'] = pd.to_numeric(df['precipitation_sum'], errors='coerce')

        # Drop rows with NaN values
        df.dropna(subset=['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum'], inplace=True)

        for index, row in df.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            temp_max = row['temperature_2m_max']
            temp_min = row['temperature_2m_min']
            temp_avg = float((temp_max + temp_min) / 2)
            precipitation = float(row['precipitation_sum'])
            season = get_season(row['date'])

            metrics.append({
                "date": date_str,
                "Precipitation": _round(precipitation),
                "Temp": _round(temp_avg),
                "MaxTemp":_round(temp_max),
                "MinTemp":_round(temp_min),
                "Season": season,
            })

        dates = [entry['date'] for entry in metrics]
        precipitation = [entry['Precipitation'] for entry in metrics]
        temp = [entry['Temp'] for entry in metrics]
        maxTemp = [entry['MaxTemp'] for entry in metrics]
        minTemp = [entry['MinTemp'] for entry in metrics]
        season = [entry['Season'] for entry in metrics]

        df = pd.DataFrame({
            "date": dates,
            "Precipitation": precipitation,
            "Temp": temp,
            "MaxTemp": maxTemp,
            "MinTemp": minTemp,
            "Season": season,
        })

        predictions = make_predictions(creek, df)

        for i, prediction in enumerate(predictions):
            metrics[i]['prediction'] = int(prediction)

        return JsonResponse(metrics, safe=False)
    else:
        return JsonResponse({'error': 'Invalid coordinates'}, safe=False)




def weather_data(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    creek = request.GET.get('creek')

    if lat and lon:
        forecast_weather = ForecastData(latitude=lat, longitude=lon, forecast_days=7)
        historical_weather = HistoricalData(latitude=lat, longitude=lon, days_back=14)

        metrics = compute_metrics(historical_weather, forecast_weather)

        dates = [entry['date'] for entry in metrics]
        today_avg_temps = [entry['today_avg_temp'] for entry in metrics]
        avg_15_day_temps = [entry['15_day_avg_temp'] for entry in metrics]
        today_precipitations = [entry['today_precipitation'] for entry in metrics]
        avg_10_day_temps = [entry['10_day_avg_temp'] for entry in metrics]
        max_rain = [entry['10_day_rain_sum'] for entry in metrics]
        # 'CDD', 'Precipitation', '15days_Median_Temp', '10days_Median_Temp', 'Max_Rain_10_Days', 'month_date', 'Temp']
        # Creating DataFrame
        df = pd.DataFrame({
            'CDD': today_avg_temps,
            'Precipitation':today_precipitations,
            '15days_Median_Temp': avg_15_day_temps,
            '10days_Median_Temp':avg_10_day_temps,
            'Max_Rain_10_Days':max_rain,
            'month_date':dates,
            'Temp':today_avg_temps
        })
        predictions = make_predictions('fallcreek',df)



        return JsonResponse(metrics, safe=False)

    return JsonResponse({'error': 'Invalid coordinates'}, status=400)





















def compute_metrics(historical_data, forecast_data):
    metrics = []

    for i in range(7):
        today = datetime.now() + timedelta(days=i)
        today_str = today.strftime('%Y-%m-%d')

        # Today's data from forecast
        today_data = forecast_data.daily_dataframe[forecast_data.daily_dataframe['date'] == today_str]
        if today_data.empty:
            continue

        today_temp_avg = float((today_data['temperature_2m_max'].values[0] + today_data['temperature_2m_min'].values[0]) / 2)
        today_precipitation = float(today_data['precipitation_sum'].values[0])

        # 15-day average temperature
        past_15_days = historical_data.daily_dataframe.tail(14)._append(today_data)
        temp_15_days_avg = float((past_15_days['temperature_2m_max'].mean() + past_15_days['temperature_2m_min'].mean()) / 2)

        # 10-day average temperature
        past_10_days = historical_data.daily_dataframe.tail(9)._append(today_data)
        temp_10_days_avg = float((past_10_days['temperature_2m_max'].mean() + past_10_days['temperature_2m_min'].mean()) / 2)

        # 10-day rain sum
        rain_10_days_sum = float(past_10_days['rain_sum'].sum())

        metrics.append({
            "date": today_str,
            "today_avg_temp": today_temp_avg,
            "15_day_avg_temp": temp_15_days_avg,
            "10_day_avg_temp": temp_10_days_avg,
            "10_day_rain_sum": rain_10_days_sum,
            "today_precipitation": today_precipitation,
            "e_coli":"None"
        })
    return metrics