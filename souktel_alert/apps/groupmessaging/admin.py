#!/usr/bin/env python
# encoding=utf-8

from django.contrib import admin

from models import *

class OutgoingLogAdmin(admin.ModelAdmin):

    list_display = ('short_text', 'sender', 'identity', 'text', 'status_text')
    list_filter = ('status', 'sender')
    ordering = [('-sent_on')]
    search_fields = ['sender', 'identity', 'text']

class SendingLogAdmin(admin.ModelAdmin):

    list_display = ('short_text', 'sender', 'groups_list', 'date')
    list_filter = ('sender', 'groups')
    ordering = [('-id')]
    search_fields = ['sender', 'groups', 'text']

class MessageAdmin(admin.ModelAdmin):

    list_display = ('name', 'code', 'site', 'short_text')
    list_filter = ('site',)
    ordering = [('-id')]
    search_fields = ['name', 'text']

class RecipientAdmin(admin.ModelAdmin):

    list_display = ('full_name', 'identity', 'site', 'active', 'backend')
    list_filter = ('site','active','backend',)
    ordering = [('-id')]
    search_fields = ['first_name', 'last_name', 'identity']

class GroupAdmin(admin.ModelAdmin):

    list_display = ('name', 'code', 'site', 'active')
    list_filter = ('site', 'active', 'managers')
    ordering = [('-id')]
    search_fields = ['code', 'name']

admin.site.register(Site)
admin.site.register(WebUser)
admin.site.register(Group, GroupAdmin)
admin.site.register(Recipient, RecipientAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(SendingLog, SendingLogAdmin)
admin.site.register(OutgoingLog, OutgoingLogAdmin)
