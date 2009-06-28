from ftw.importer.models import *
from django.contrib import admin

class EventsAdmin(admin.ModelAdmin):
    list_display = ('date','state',)
    list_filter = ('date', 'state')
    ordering = ['-id']

admin.site.register(Events, EventsAdmin)