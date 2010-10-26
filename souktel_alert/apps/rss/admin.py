from django.contrib import admin

from models import *


class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description','group', 'creator', 'pupdate')
    list_filter = ('title', 'creator', 'pupdate')
    search_fields = ('title',)
    ordering = ('-pupdate',)

admin.site.register(NewsFeed, NewsFeedAdmin)

