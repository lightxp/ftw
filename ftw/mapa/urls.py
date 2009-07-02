from django.conf.urls.defaults import *

urlpatterns = patterns('ftw.mapa.views',
    (r'^$', 'index'), 
    (r'^index/$', 'index'), 
)