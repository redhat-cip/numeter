"""
wide_storage urls module.
"""

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^hosts$', 'wide_storage.views.hosts', name='wide-storage-hosts'),
    url(r'^hinfo$', 'wide_storage.views.hinfo', name='wide-storage-hinfo'),
    url(r'^list$', 'wide_storage.views.list', name='wide-storage-list'),
    url(r'^info$', 'wide_storage.views.info', name='wide-storage-info'),
    url(r'^data$', 'wide_storage.views.data', name='wide-storage-data'),
)
