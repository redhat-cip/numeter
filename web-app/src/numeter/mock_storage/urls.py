from django.conf.urls import patterns


urlpatterns = patterns('',
    url(r'^hosts$', 'moch_storage.views.hosts'),
    url(r'^hinfo$', 'moch_storage.views.hinfo'),
    url(r'^list$', 'moch_storage.views.list'),
	url(r'^data$', 'moch_storage.views.data'),
)
