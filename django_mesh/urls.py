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

#Django imports
from django.conf.urls import patterns, url

from .views import IndexView, ChannelIndexView, ChannelDetailView, PostIndexView, PostDetailView, TagDetailView, TagIndexView, FileDetailView, FileIndexView, OembedDetailView
from django_mesh import views

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name="mesh_index"),
    url(r'^channels/$', ChannelIndexView.as_view(), name="mesh_channel_index"),
    url(r'^channels/(?P<slug>.*)/$', ChannelDetailView.as_view(), name="mesh_channel_view"),
    url(r'^follow/(?P<slug>.*)/$', views.self_enrollment, name="mesh_follow_channel"),
    url(r'^posts/$', PostIndexView.as_view(), name="mesh_post_index"),
    url(r'^posts/(?P<slug>.+)/$', PostDetailView.as_view(), name="mesh_post_view"),
    url(r'^tags/$', TagIndexView.as_view(), name="mesh_tag_index"),
    url(r'^tags/(?P<slug>.+)/$', TagDetailView.as_view(), name="mesh_tag_view"),
    url(r'^file/$', FileIndexView.as_view(), name="mesh_file_index"),
    url(r'^file/(?P<slug>.+)/$', FileDetailView.as_view(), name="mesh_file_view"),
    url(r'^oembed/file/(?P<slug>.+)/$', OembedDetailView.as_view(), name="mesh_oembed"),
)
