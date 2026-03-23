from django.urls import path

from src.age_verification import views

urlpatterns = [
    path('country-restricted', views.country_restricted, name='age_verification.country_restricted'),
]
