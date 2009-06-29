from django.conf.urls.defaults import *

urlpatterns = patterns('ftw.exporter.views',
    (r'^ulice/(?P<ulica_name>.+)/$', 'completeStreets'),
)