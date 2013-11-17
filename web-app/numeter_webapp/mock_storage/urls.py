from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^([12]/?)?$', 'mock_storage.views.index'),
    url(r'^(?P<id>[12])/hosts$', 'mock_storage.views.hosts'),
    url(r'^(?P<id>[12])/hinfo$', 'mock_storage.views.hinfo'),
    url(r'^(?P<id>[12])/list$', 'mock_storage.views.list'),
    url(r'^(?P<id>[12])/data$', 'mock_storage.views.data'),
)
