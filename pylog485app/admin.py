from django.contrib import admin

from pylog485app.models import Reading, Conf, Monitor

class ReadingAdmin(admin.ModelAdmin):
    list_display = ('data','meta')

class ConfAdmin(admin.ModelAdmin):
    list_display = ('data','meta')

class MonitorAdmin(admin.ModelAdmin):
    list_display = ('data','meta')


admin.site.register(Reading, ReadingAdmin)
admin.site.register(Conf, ConfAdmin)
admin.site.register(Monitor, MonitorAdmin)
