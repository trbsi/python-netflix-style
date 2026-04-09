from django.urls import path

from . import views

urlpatterns = [
    path('commands', views.commands, name='admin.commands'),
    path('trigger/import-partial', views.trigger_partial_import, name='admin.trigger_import_partial'),
    path('trigger/frontend', views.trigger_generate_frontend, name='admin.trigger_generate_frontend'),
    path('trigger/sitemap-partial', views.trigger_sitemap_partial, name='admin.trigger_sitemap_partial'),
    path('trigger/title-rewrite', views.trigger_title_rewrite, name='admin.trigger_title_rewrite'),
]
