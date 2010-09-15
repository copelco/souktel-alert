from django.contrib import admin

from goals import models as goals


class GoalAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact', 'body', 'date_created',
                    'date_last_notified', 'in_session', 'complete')
    list_filter = ('complete', 'in_session', 'date_created',
                   'date_last_notified')
    search_fields = ('body',)
    ordering = ('-date_created',)
admin.site.register(goals.Goal, GoalAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'goal', 'body', 'date',)
    list_filter = ('date',)
    ordering = ('-date',)
    search_fields = ('body', 'goal__body')
admin.site.register(goals.Answer, AnswerAdmin)
