from django.contrib import admin

from goals import models as goals


class GoalAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'connection', 'body')
    list_filter = ('date',)
    search_fields = ('body',)
admin.site.register(goals.Goal, GoalAdmin)


class SessionAdmin(admin.ModelAdmin):
    pass
admin.site.register(goals.Session, SessionAdmin)


class AnswerAdmin(admin.ModelAdmin):
    pass
admin.site.register(goals.Answer, AnswerAdmin)
