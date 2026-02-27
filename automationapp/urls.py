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
from django.conf import settings
from automationapp import settings as local_settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = (
        [
            path('', include('src.core.urls')),
            path('notification/', include('src.notification.urls')),
            path('accounts/', include('allauth.urls')),
            path('user/', include('src.user.urls')),
            path('media/', include('src.media.urls')),
            path('.privatnomjesto/', admin.site.urls),
        ]
)

if local_settings.DEBUG:
    urlpatterns += static(local_settings.STATIC_URL, document_root=local_settings.STATICFILES_DIRS[0])