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

from django.contrib import admin
from models import *

admin.site.register(Channel)

class ItemAdmin(admin.TabularInline):
	model = Item
	extra = 0

class PostAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("title",)}
	inlines = [ItemAdmin]

admin.site.register(Post, PostAdmin)

admin.site.register(Item)
