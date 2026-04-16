from django.contrib.sitemaps import views as sitemaps_views
from django.urls import path

from src.sitemap.sitemaps import CategorySitemap, StaticViewSitemap, VideosSitemap

sitemaps = {
    'categories': CategorySitemap,
    'static-views': StaticViewSitemap,
    'videos': VideosSitemap,
}

urlpatterns = [
    path(
        "sitemap.xml", sitemaps_views.index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index"
    ),
    path(
        "sitemap-<section>.xml",
        sitemaps_views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap"
    ),
]
