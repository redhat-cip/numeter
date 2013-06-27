from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'core.views.index', name='index'),
    url(r'^login$', 'core.views.login', name='login'),
    url(r'^logout$', 'core.views.logout', name='logout'),
    url(r'^multiviews$', 'core.views.multiviews_index', name='multiviews'),
    url(r'^settings$', 'core.views.configuration_index', name='settings'),

    url(r'^get/hosts/(?P<id>\w+)$', 'core.views.get_hosts'),

    # url(r'^numeter/', include('numeter.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
