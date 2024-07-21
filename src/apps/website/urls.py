from django.urls import path
from .views import (HomePageView ,weather_data ,EagleCreekPageView ,
                    FallCreekPageView,WhiteCreekPageView,LickCreekPageView)

app_name = 'website'
urlpatterns=[

    path('',HomePageView.as_view(),name='home'),
    path('weather-data/', weather_data, name='weather_data'),
    path('eaglecreek/', EagleCreekPageView.as_view(), name='eaglecreek'),
    path('fallcreek/', FallCreekPageView.as_view(), name='fallcreek'),
    path('whitecreek/', WhiteCreekPageView.as_view(), name='whitecreek'),
    path('lickcreek/', LickCreekPageView.as_view(), name='lickcreek'),

]