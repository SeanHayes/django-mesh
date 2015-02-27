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
import logging

# Django imports
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.sites.shortcuts import get_current_site

import json

# App imports
from .models import Channel, Post, Tag, Media

#test upload
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse, resolve


from .forms import UploadForm

logger = logging.getLogger(__name__)

class IndexView(ListView):
    model = Post
    template_name = 'django_mesh/index.html'
    context_object_name = 'post_list'
    paginate_by = 50

    def get_queryset(self, *args, **kwargs):
        ret = super(IndexView, self).get_queryset(*args, **kwargs)
        return ret.get_for_user(user=self.request.user).active()

class ChannelIndexView(ListView):
    model = Channel
    template_name = 'django_mesh/channel_index.html'
    context_object_name = 'channel_list'
    paginate_by = 50

    def get_queryset(self, *args, **kwargs):
        qs = super(ChannelIndexView, self).get_queryset(*args, **kwargs)
        return qs.get_for_user(self.request.user)

class ChannelDetailView(ListView):
    model = Post
    template_name = 'django_mesh/channel_view.html'
    context_object_name = 'post_list'
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        self.channel = get_object_or_404(Channel.objects.get_for_user(user=self.request.user), slug=self.kwargs['slug'])
        response = super(ChannelDetailView, self).dispatch(request, *args, **kwargs)
        return response

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        ret = super(ChannelDetailView, self).get_queryset(*args, **kwargs)

        if ((self.channel.public) or (user in self.channel.followers.all())):
            return ret.filter(channel=self.channel).active()
        else:
            return ret.none()

    def get_context_data(self, **kwargs):
        context = super(ChannelDetailView, self).get_context_data(**kwargs)
        context['channel'] = self.channel
        return context

class PostIndexView(ListView):
    model = Post
    template_name = 'django_mesh/post_index.html'
    context_object_name = 'post_list'
    paginate_by = 50

    def get_queryset(self, *args, **kwargs):
        ret = super(PostIndexView, self).get_queryset(*args, **kwargs)
        return ret.get_for_user(user=self.request.user).active()

class PostDetailView(DetailView):
    model = Post
    template_name = 'django_mesh/post_view.html'
    context_object_name = 'post'

    def get_queryset(self, *args, **kwargs):
        ret = super(PostDetailView, self).get_queryset(*args, **kwargs)
        return ret.get_for_user(user=self.request.user).active()

class TagDetailView(ListView):
    model = Post
    template_name = 'django_mesh/tag_view.html'
    context_object_name = 'post_list'
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):

        self.tag = get_object_or_404(Tag.objects.all(), slug=kwargs['slug'])
        response = super(TagDetailView, self).dispatch(request, *args, **kwargs)
        return response

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        ret = super(TagDetailView, self).get_queryset(*args, **kwargs).get_for_user(user).filter(tags=self.tag).distinct()

        if len(ret) == 0:
            raise Http404
        return ret

    def get_context_data(self, **kwargs):
        context = super(TagDetailView, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

class TagIndexView(ListView):
    model = Tag
    template_name = 'django_mesh/tag_index.html'
    context_object_name = 'tag_list'

    def get_queryset(self, *args, **kwargs):
        qs = super(TagIndexView, self).get_queryset(*args, **kwargs)
        return qs.get_for_user(self.request.user)

class MediaDetailView(DetailView):
    model = Media
    template_name = 'django_mesh/media_view.html'

    def get_queryset(self, *args, **kwargs):
        qs = super(MediaDetailView, self).get_queryset(*args, **kwargs)
        return qs.get_for_user(self.request.user)


class MediaIndexView(ListView):
    model = Media
    template_name = 'django_mesh/media_index_view.html'

    def get_queryset(self, *args, **kwargs):
        qs = super(MediaIndexView, self).get_queryset(*args, **kwargs)
        return qs.get_for_user(self.request.user)

def self_enrollment(request, *args, **kwargs):
    user = request.user
    if request.method == 'POST':
        channel = get_object_or_404(Channel.objects.get_for_user(user), slug=kwargs['slug'])
        channel.followers.add(user)
        return HttpResponseRedirect(reverse('mesh_channel_index'))
    else:
        return HttpResponseRedirect(reverse('mesh_channel_index'))

class OembedDetailView(DetailView):

    model = Media

    @property
    def get_site_domain(request):
        return get_current_site(request).domain


    def dispatch(self, request, *args, **kwargs):
        self.media = get_object_or_404(Media.objects.get_for_user(user=self.request.user), slug=self.kwargs['slug'])

        user = request.user

        file_dict = {}

        file_dict['version'] = 1.0
        file_dict['title'] = self.media.title
        file_dict['url'] = self.media.get_file_url
        file_dict['provider_name'] = self.get_site_domain

        if self.media.media_type == Media.MEDIA_TYPE.IMAGE:
            file_dict['type'] = 'photo'
            file_dict['width'] = 240
            file_dict['height'] = 160

        elif self.media.media_type == Media.MEDIA_TYPE.VIDEO:
            file_dict['type'] = 'video'
            file_dict['html'] = self.media.oembed_html
            file_dict['height'] = 350
            file_dict['width'] = 700

        return HttpResponse(json.dumps([file_dict]), content_type="application/json")
