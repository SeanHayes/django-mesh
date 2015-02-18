# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Django imports
from django.core.urlresolvers import reverse
from datetime import date, timedelta
# Test imports
from .util import BaseTestCase

# App imports
from ..models import Post

class SitemapIndexTestCase(BaseTestCase):
    def test_items_returned(self):
        self.c1.save()
        self.c3.save()
        self.p1.channel = self.c1
        self.p1.save()

        self.p2.channel = self.c3
        self.p2.save()

        self.p3.channel = self.c1
        self.p3.save()

        response = self.client.get(reverse('sitemap'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sitemap-channel")
        self.assertContains(response, "sitemap-tag")
        self.assertContains(response, "sitemap-post")

class PostSitemapsTestCase(BaseTestCase):

    def test_items_returned(self):
        domain_name = 'http://example.com/'
        sub_name = 'blog/'
        channel = 'posts/'

        self.c1.save()
        self.c3.save()
        self.t1.save()
        self.t2.save()

        self.p1.channel = self.c1
        self.p1.save()
        self.p1.tags.add(self.t1)
        self.p1.published = date.today()

        self.p2.channel = self.c3
        self.p2.save()
        self.p2.tags.add(self.t2)

        self.p3.channel = self.c1
        self.p3.save()
        self.p3.tags.add(self.t2)

        response = self.client.get(reverse('sitemaps', kwargs={'section': 'post'}))

        self.assertContains(response, '<loc>%(dn)s%(sn)s%(c)s%(slug)s/</loc>' %{"dn":domain_name, "sn":sub_name, "c":channel, "slug": self.p1.slug})
        self.assertNotContains(response, '<loc>%(dn)s%(sn)s%(c)s%(slug)s/</loc>' %{"dn":domain_name, "sn":sub_name, "c":channel, "slug": self.p2.slug})
#       possible tags in sitemap page
        self.assertContains(response, '<changefreq>')
        self.assertContains(response, '<priority>')
        self.assertContains(response, '<lastmod>')

        self.assertContains(response, '<news:keywords>')
        self.assertContains(response, '<news:publication_date>')
        self.assertContains(response, '<news:title>')
        self.assertContains(response, '<news:publication>')

#       p1 tags should be in there
        self.assertContains(response, self.p1.title) #<news:title>
        self.assertContains(response, self.t1.title )  #<news:keywords>
        self.assertContains(response, self.p1.published) #<news:publication_date>

#       p2 tags should not, since its put in a private channel
        self.assertNotContains(response, self.p2.title)
        self.assertNotContains(response, self.t2.title )  #<news:keywords>

        self.assertNotContains(response, self.p3.title)

class ChannelSitemapsTestCase(BaseTestCase):
    def test_items_returned(self):
        self.c1.save()
        self.c3.save()

        response = self.client.get(reverse('sitemaps', kwargs={'section': 'channel'}))

        self.assertContains(response, self.c1.title)
        self.assertNotContains(response, self.c3.title)

class TagSitemapsTestCase(BaseTestCase):
    def test_items_returned(self):

        self.c1.save()
        self.c2.save()
        self.p1.channel = self.c1
        self.p2.channel = self.c2
        self.p1.save()
        self.p2.save()

        self.t1.save()
        self.t2.save()

        self.p1.tags.add(self.t1)
        self.p2.tags.add(self.t2)

        response = self.client.get(reverse('sitemaps', kwargs={'section': 'tag'}))

        self.assertContains(response, self.t1.title)