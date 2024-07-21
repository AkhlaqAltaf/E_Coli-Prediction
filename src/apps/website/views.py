import pandas as pd
from django.http import JsonResponse
from django.views.generic import TemplateView
from src.apps.website.weather_analyser.forcast_data import ForecastData
from src.apps.website.weather_analyser.historical_data import HistoricalData
from datetime import datetime, timedelta

from src.apps.website.weather_analyser.predictions import PredictEColi

import numpy as np


class HomePageView(TemplateView):
    template_name = "website/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class EagleCreekPageView(TemplateView):
    template_name = "eaglecreek.html"

class FallCreekPageView(TemplateView):
    template_name = "fallcreek.html"

class LickCreekPageView(TemplateView):
    template_name = "lickcreek.html"

class WhiteCreekPageView(TemplateView):
    template_name = "whitecreek.html"


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
        predictions = PredictEColi()
        response = predictions.predict('fallcreek',df)
        print(response)



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
    print(metrics)
    return metrics