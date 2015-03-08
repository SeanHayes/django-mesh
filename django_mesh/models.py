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

# Python imports
from __future__ import unicode_literals
import re
import six
# Django imports
#from django.contrib.sitemaps import ping_google
from django.utils.encoding import python_2_unicode_compatible

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.conf import settings


# 3d party imports
from model_utils import Choices
import markdown
import textile # to do: add oembed for textile markup
from pyembed.markdown import PyEmbedMarkdown
from pyembed.core import PyEmbed
from bs4 import BeautifulSoup

# App imports
from .managers import PostQuerySet, ChannelQuerySet, TagQuerySet, MediaQuerySet

# URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
URL_REGEX = r"""http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"""

# def get_match_and_replace(text):

#     # for each in re.findall(URL_REGEX, text):
#     #     text = text.replace(each, '<a href="%s">%s</a>' % (each,each), 1)
#     # return text # text but with anchors inserted


@python_2_unicode_compatible
class _Abstract(models.Model):     #microblog compatible.
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=140, unique=True)
    text = models.TextField(default='')
    rendered_text = models.TextField(default='', blank=True)
    TEXT_TYPE = Choices(
        (0, 'SIMPLE', 'Simple',),
        (1, 'MARKDOWN', 'Markdown',),
        (2, 'TEXTILE', 'Textile'),
        )

    text_type      = models.IntegerField(max_length=1, default=TEXT_TYPE.SIMPLE, choices=TEXT_TYPE)

    def render(self, *args, **kwargs):

        self.rendered_text = markdown.markdown(self.text)

        if self.text_type == self.TEXT_TYPE.SIMPLE:
            self.rendered_text = self.text

        elif self.text_type == self.TEXT_TYPE.TEXTILE:
            self.rendered_text = textile.textile(self.text)


        soup = BeautifulSoup(self.rendered_text)

        matching_text_nodes = soup.find_all(text = re.compile(URL_REGEX)) 

        pyembed = PyEmbed()


        for matching_text_node in matching_text_nodes:

            plain_text = six.text_type(matching_text_node)

            for each in re.findall(URL_REGEX, plain_text):
                plain_text = plain_text.replace(each, '<a href="%s">%s</a>' % (each,each), 1)

            if matching_text_node.parent.text == each: # if url on one line, each == url == matching_text_node
                try:
                    oembed = pyembed.embed(matching_text_node)
                except:
                    matching_text_node.replace_with(plain_text)
                else:
                    matching_text_node.replace_with(oembed)
            else:
                matching_text_node.replace_with(plain_text)

        soup = BeautifulSoup(soup.encode(formatter=None))

        self.rendered_text = soup.encode(formatter=None).decode()

    def save(self, *args, **kwargs):
        if self.rendered_text == '':
            self.render()

        super(_Abstract, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True

class Channel(_Abstract):
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL)

    ENROLLMENTS = Choices(
        (0, 'SELF', 'Self'),
        (1, 'AUTHOR', 'Author'),
    )

    public = models.BooleanField(default=True, help_text="If False, only followers will be able to see content.")

    enrollment = models.IntegerField(max_length=1, default=ENROLLMENTS.SELF, choices=ENROLLMENTS)

    objects = ChannelQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('mesh_channel_view', kwargs={'slug': self.slug,})

    class Meta:
        ordering = ['title']

class Tag(_Abstract):

    objects = TagQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('mesh_tag_view', kwargs={'slug': self.slug,})

class Post(_Abstract):

    SUMMARY_LENGTH = 50

    STATUSES = Choices(
        (0, 'DRAFT',     'Draft',),
        (1, 'PUBLISHED', 'Published',),
    )

    channel         = models.ForeignKey(Channel)
    author          = models.ForeignKey(settings.AUTH_USER_MODEL)
    status          = models.IntegerField(max_length=1, default=STATUSES.DRAFT, choices=STATUSES)
    custom_summary  = models.TextField(default='')
    created         = models.DateTimeField(auto_now_add=True, editable=False)
    modified        = models.DateTimeField(auto_now=True, editable=False)
    published       = models.DateTimeField(default=timezone.now)

    tags = models.ManyToManyField(Tag)

    objects = PostQuerySet.as_manager()

    def _get_teaser(self):
        "A small excerpt of text that can be used in the absence of a custom summary."
        return self.text[:Post.SUMMARY_LENGTH]

    teaser = property(_get_teaser)

    def _get_summary(self):
        "Returns custom_summary, or teaser if not available."
        if len(self.custom_summary) > 0:
            return self.custom_summary
        else:
            return self.teaser

    summary = property(_get_summary)

    def get_absolute_url(self):
        return reverse('mesh_post_view', kwargs={'slug': self.slug,})

    class Meta:
        ordering = ['published']

class MockYoutube(models.Model):
    ysc = models.IntegerField(max_length=3)
    yu = models.CharField(max_length=140, unique=True)
    yc = models.CharField(max_length=140, unique=True)
    yt = models.TextField(default='')
    yh = models.CharField(max_length=140, unique=True)

    yosc = models.IntegerField(max_length=3)
    you = models.CharField(max_length=140, unique=True)
    yoh = models.CharField(max_length=140, unique=True)
    yot = models.TextField(default='')
    yoj = models.TextField(default='')

class Media(_Abstract):

    MEDIA_TYPES = Choices(
        (0, 'NONE',       'none',),
        (1, 'IMAGE',      'image',),
        (2, 'VIDEO',      'video',),
    )

    channel = models.ForeignKey(Channel)
    objects = MediaQuerySet.as_manager()

    upload_file = models.FileField(upload_to='uploads/%Y/%m/%d')

    media_type = models.IntegerField(max_length=1, default=MEDIA_TYPES.NONE, choices=MEDIA_TYPES)

    oembed_html = models.TextField(default='', blank=True)

    media_height = models.SmallIntegerField(null=True)
    media_width = models.SmallIntegerField(null=True)

    thumbnail_height = models.SmallIntegerField(default=120)
    thumbnail_width = models.SmallIntegerField(default=200)

    @property    
    def file_url(self):
        return self.upload_file.url

    def render(self):

        embed = '<a href="%s"> %s </a>' % (self.file_url, self.file_url)

        if self.media_type == Media.MEDIA_TYPES.IMAGE:
            embed = '<img src="%s" style="width:%d%%; height:%d%%;>' % (self.file_url, self.media_width, self.media_height)

        elif self.media_type == Media.MEDIA_TYPES.VIDEO:
            embed = '<video width="%d" height="%d" controls> <source src="%s" type="video/mp4"> Your browser does not support the video tag. </video>' % (self.media_width, self.media_height, self.file_url)

        self.oembed_html = embed

    def get_absolute_url(self):
        return reverse('mesh_media_view', kwargs={'slug': self.slug,})
