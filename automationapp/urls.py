"""
URL configuration for automationapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import_dump:  from my_app import_dump views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import_dump:  from other_app.views import_dump Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import_dump include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views as sitemaps_views
from django.urls import path, include

from automationapp import settings as local_settings
from src.core.sitemaps import VideoSitemap, CategorySitemap

sitemaps = {
    'videos': VideoSitemap,
    'categories': CategorySitemap,
}
urlpatterns = (
    [
        path('', include('src.core.urls')),
        path('notification/', include('src.notification.urls')),
        path('accounts/', include('allauth.urls')),
        path('user/', include('src.user.urls')),
        path('movies/', include('src.media.urls')),
        path('.privatniadmin/', include('src.myadmin.urls')),
        path('.privatnomjesto/', admin.site.urls),
        path("sitemap.xml", sitemaps_views.index, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.index"),
        path("sitemap-<section>.xml", sitemaps_views.sitemap, {"sitemaps": sitemaps},
             name="django.contrib.sitemaps.views.sitemap"),
    ]
)

if local_settings.DEBUG:
    urlpatterns += static(local_settings.STATIC_URL, document_root=local_settings.STATICFILES_DIRS[0])
