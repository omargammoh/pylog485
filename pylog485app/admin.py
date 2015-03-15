from django.contrib import admin

from pylog485app.models import Readings, Conf, Monitor

class ReadingsAdmin(admin.ModelAdmin):
    list_display = ('data','meta')

class ConfAdmin(admin.ModelAdmin):
    list_display = ('data','meta')

class MonitorAdmin(admin.ModelAdmin):
    list_display = ('data','meta')


admin.site.register(Readings, ReadingsAdmin)
admin.site.register(Conf, ConfAdmin)
admin.site.register(Monitor, MonitorAdmin)
