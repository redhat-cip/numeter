from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^hosts$', 'mock_storage.views.hosts'),
    url(r'^hinfo$', 'mock_storage.views.hinfo'),
    url(r'^list$', 'mock_storage.views.list'),
    url(r'^data$', 'mock_storage.views.data'),
)
