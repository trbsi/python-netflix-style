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
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from automationapp import settings as local_settings

urlpatterns = (
    [
        path('', include('src.core.urls')),
        path('notification/', include('src.notification.urls')),
        path('accounts/', include('allauth.urls')),
        path('chat/', include('src.chat.urls')),
        # path('user/', include('src.user.urls')), not used for now
        path('movies/api/', include('src.media.urls_api')),
        path('sitemaps2/', include('src.sitemap.urls')),
        path('.privatniadmin/', include('src.myadmin.urls')),
        path('.privatnomjesto/', admin.site.urls),
    ]
)
urlpatterns += i18n_patterns(
    path('movies/', include('src.media.urls')),
)

if local_settings.DEBUG:
    urlpatterns += static(local_settings.STATIC_URL, document_root=local_settings.STATICFILES_DIRS[0])
