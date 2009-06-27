from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ftw/', include('ftw.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/importer/importprzystankow/', 'ftw.importer.admin_views.importuj_przystanek'),
    (r'^admin/importer/importulic/', 'ftw.importer.admin_views.importuj_ulice'),
    (r'^admin/importer/importtras/', 'ftw.importer.admin_views.importuj_trasy'),
    (r'^admin/', include(admin.site.urls)),
)
