from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ftw/', include('ftw.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^fe_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^$', 'ftw.mapa.views.index'),     
    (r'^mapa/', include('ftw.mapa.urls')),
    (r'^admin/importer/', include('ftw.importer.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^exporter/', include('ftw.exporter.urls')),
)
