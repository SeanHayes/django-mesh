from django.contrib.sitemaps import GenericSitemap

from django.contrib.sitemaps import Sitemap
from django_mesh.models import Post, Channel, Tag
from django.contrib.sites.models import Site

class PostSitemap(Sitemap):
    changefreq = "always"
    priority = 0.9

    def items(self):
        return Post.objects.active().filter(channel__public=True)

    def lastmod(self, obj):
        return obj.modified

    @property
    def name(self):
        site = Site.objects.get_current()
        return site

class ChannelSitemap(Sitemap):
    changefreq="always"
    priority = 0.5

    def items(self):
        return Channel.objects.filter(public=True)

class TagSitemap(Sitemap):
    changefreq="always"
    priority = 0.5

    def items(self):
        return Tag.objects.filter(post__channel__public=True)