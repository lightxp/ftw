from django.conf.urls.defaults import *

urlpatterns = patterns('ftw.exporter.views',
    (r'^podpowiedz/$', 'completeBusStops'),
)