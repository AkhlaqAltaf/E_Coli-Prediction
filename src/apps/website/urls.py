from django.urls import path
from .views import (HomePageView ,predictions,CreekPageView,historical_predictions)

app_name = 'website'
urlpatterns=[

    path('',HomePageView.as_view(),name='home'),
    path('weather-data/', predictions, name='weather_data'),
    path('creekname/<str:creekname>', CreekPageView.as_view(), name='creekname'),
    path('historical/', historical_predictions, name='historical_data'),  # New URL pattern

]