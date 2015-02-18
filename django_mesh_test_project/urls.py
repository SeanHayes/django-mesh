from django.conf.urls import patterns, include, url

from .sitemaps import PostSitemap, ChannelSitemap, TagSitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
admin.autodiscover()

sitemaps = {
    'post':PostSitemap,
    'channel':ChannelSitemap,
    'tag':TagSitemap
}

urlpatterns = patterns('',
    url(r'^blog/', include('django_mesh.urls')),

    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}, name='sitemap'),

    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps,
                                                                                     'template_name': "sitemaps.html"
    }, name='sitemaps'),
    url(r'^admin/', include(admin.site.urls)),
)