#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from decisiontree.models import *


class TransitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_state', 'answer', 'next_state')
    list_filter = ('answer',)
    ordering = ('current_state',)


class TaggerAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer',)


admin.site.register(Tree)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(TreeState)
admin.site.register(Transition, TransitionAdmin)
admin.site.register(Entry)
admin.site.register(Session)
admin.site.register(Tagger, TaggerAdmin)


