from django.contrib import admin

from models import *


class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description','group', 'creator', 'pub_date')
    list_filter = ('title', 'creator', 'pub_date')
    search_fields = ('title',)
    ordering = ('-pub_date',)

admin.site.register(NewsFeed, NewsFeedAdmin)

