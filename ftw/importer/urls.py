from django.conf.urls.defaults import *

urlpatterns = patterns('ftw.importer.admin_views',
    (r'^importprzystankow/$', 'importuj_przystanek'),
    (r'^importulic/$', 'importuj_ulice'),
    (r'^importtras/$', 'importuj_trasy'), 
)