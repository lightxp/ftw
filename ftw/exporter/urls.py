from django.conf.urls.defaults import *

urlpatterns = patterns('ftw.exporter.views',
    (r'^podpowiedz/$', 'completeBusStops'),
    (r'^przystanki/autobusy/$', 'completeBusStopsXML', {'typIn':'A'}),
    (r'^przystanki/tramwaje/$', 'completeBusStopsXML', {'typIn':'T'}),
    (r'^przystanki/nocne/$', 'completeBusStopsXML', {'typIn':'N'}),
    (r'^przystanki/najblizsze/(?P<lat>\d{2}\.\d+)/(?P<lng>\d{2}\.\d+)/$', 'completeNearest', {'distance_max': 0.5}),
    (r'^linie/$', 'trasy'),
    (r'^trasa/(?P<fromway_lat>\d{2}\.\d+)/(?P<fromway_lng>\d{2}\.\d+)/(?P<toway_lat>\d{2}\.\d+)/(?P<toway_lng>\d{2}\.\d+)/$', 'findWay'),
)