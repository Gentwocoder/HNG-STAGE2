from django.urls import path
from . import views

urlpatterns = [
    path('refresh', views.refresh_countries, name='refresh_countries'),
    path('image', views.get_summary_image, name='summary_image'),
    path('', views.list_countries, name='list_countries'),
    path('<str:name>', views.country_detail, name='country_detail'),
]