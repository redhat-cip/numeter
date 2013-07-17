from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^([12]/?)?$', 'mock_storage.views.index'),
    url(r'^(?P<id>[12])/numeter-storage/hosts$', 'mock_storage.views.hosts'),
    url(r'^(?P<id>[12])/numeter-storage/hinfo$', 'mock_storage.views.hinfo'),
    url(r'^[12]/numeter-storage/list$', 'mock_storage.views.list'),
    url(r'^[12]/numeter-storage/data$', 'mock_storage.views.data'),
)
