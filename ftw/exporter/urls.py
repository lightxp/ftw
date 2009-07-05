from django.conf.urls.defaults import *

urlpatterns = patterns('ftw.exporter.views',
    (r'^podpowiedz/$', 'completeBusStops'),
    (r'^przystanki/autobusy/$', 'completeBusStopsXML', {'typIn':'A'}),
    (r'^przystanki/tramwaje/$', 'completeBusStopsXML', {'typIn':'T'}),
    (r'^przystanki/nocne/$', 'completeBusStopsXML', {'typIn':'N'}),
)