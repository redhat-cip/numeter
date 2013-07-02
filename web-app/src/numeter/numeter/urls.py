from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'core.views.index', name='index'),
    url(r'^apropos$', 'core.views.apropos', name='apropos'),
    url(r'^login$', 'core.views.login', name='login'),
    url(r'^logout$', 'core.views.logout', name='logout'),

    url(r'^multiviews$', 'core.views.multiviews_index', name='multiviews'),

    url(r'^configuration$', 'core.views.configuration_index', name='configuration'),
    url(r'^configuration/profile$', 'core.views.profile_index', name='profile index'),
    url(r'^configuration/profile/(?P<user_id>\d+)/update$', 'core.views.update_profile', name='update profile'),
    url(r'^configuration/profile/(?P<user_id>\d+)/update_password$', 'core.views.update_password', name='update password'),

    url(r'^configuration/storage$', 'core.views.storage_index', name='storage index'),
    url(r'^configuration/storage/add$', 'core.views.storage_add', name='storage add'),
    url(r'^configuration/storage/(?P<storage_id>\d+)$', 'core.views.storage_get', name='storage'),
    url(r'^configuration/storage/(?P<storage_id>\d+)/update$', 'core.views.storage_update', name='storage update'),
    url(r'^configuration/storage/(?P<storage_id>\d+)/delete$', 'core.views.storage_delete', name='storage delete'),

    url(r'^get/hosts/(?P<id>\w+)?$', 'core.views.get_hosts_by_group'),
    url(r'^get/plugins/(?P<id>\w+)?$', 'core.views.get_plugins_by_host'),

    # url(r'^numeter/', include('numeter.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
