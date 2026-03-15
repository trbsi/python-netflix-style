from django.urls import path

from . import views

urlpatterns = [
    path('trigger/import', views.trigger_import, name='admin.trigger_import'),
    path('trigger/frontend', views.trigger_generate_frontend, name='admin.trigger_generate_frontend'),
]
