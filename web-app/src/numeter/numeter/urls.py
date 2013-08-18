from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.index', name='index'),
    url(r'^apropos$', 'core.views.apropos', name='apropos'),
    url(r'^login$', 'core.views.auth.login', name='login'),
    url(r'^logout$', 'core.views.auth.logout', name='logout'),

    url(r'^get/graph/(?P<host_id>\d+)/(?P<plugin>.+)$', 'core.views.hosttree.get_data', name='plugin'),

    url(r'^configuration$', 'core.views.configuration_index', name='configuration'),
    url(r'^configuration/profile$', 'core.views.profile_index', name='profile index'),
    url(r'^configuration/profile/(?P<user_id>\d+)/update$', 'core.views.update_profile', name='update profile'),
    url(r'^configuration/profile/(?P<user_id>\d+)/update_password$', 'core.views.update_password', name='update password'),

    url(r'^configuration/user$', 'core.views.configuration.user_index', name='user index'),
    url(r'^configuration/user/list$', 'core.views.configuration.user_list', name='user list'),
    url(r'^configuration/superuser/list$', 'core.views.configuration.superuser_list', name='superuser list'),
    url(r'^configuration/user/add$', 'core.views.configuration.user_add', name='user add'),
    url(r'^configuration/user/(?P<user_id>\d+)$', 'core.views.configuration.user_get', name='user'),
    url(r'^configuration/user/(?P<user_id>\d+)/update$', 'core.views.configuration.user_update', name='user update'),
    url(r'^configuration/user/(?P<user_id>\d+)/delete$', 'core.views.configuration.user_delete', name='user delete'),
    url(r'^configuration/group/list$', 'core.views.configuration.group_list', name='group list'),
    url(r'^configuration/group/add$', 'core.views.configuration.group_add', name='group add'),
    url(r'^configuration/group/(?P<group_id>\d+)$', 'core.views.configuration.group_get', name='group'),
    url(r'^configuration/group/(?P<group_id>\d+)/update$', 'core.views.configuration.group_update', name='group update'),
    url(r'^configuration/group/(?P<group_id>\d+)/delete$', 'core.views.configuration.group_delete', name='group delete'),

    url(r'^configuration/storage$', 'core.views.configuration.storage_index', name='storage index'),
    url(r'^configuration/storage/list$', 'core.views.configuration.storage_list', name='storage list'),
    url(r'^configuration/storage/add$', 'core.views.configuration.storage_add', name='storage add'),
    url(r'^configuration/storage/(?P<storage_id>\d+)$', 'core.views.configuration.storage_get', name='storage'),
    url(r'^configuration/storage/(?P<storage_id>\d+)/update$', 'core.views.configuration.storage_update', name='storage update'),
    url(r'^configuration/storage/(?P<storage_id>\d+)/delete$', 'core.views.configuration.storage_delete', name='storage delete'),
    url(r'^configuration/storage/(?P<storage_id>\d+)/create_hosts$', 'core.views.configuration.storage_create_hosts', name='storage create hosts'),
    url(r'^configuration/storage/bad_hosts$', 'core.views.configuration.storage_bad_hosts', name='storage bad hosts'),

    url(r'^configuration/host/list$', 'core.views.configuration.host_list', name='host list'),
    url(r'^configuration/host/list/delete$', 'core.views.configuration.host.bulk_delete', name='host bulk delete'),
    url(r'^configuration/host/(?P<host_id>\d+)$', 'core.views.configuration.host_get', name='host'),
    url(r'^configuration/host/(?P<host_id>\d+)/update$', 'core.views.configuration.host_update', name='host update'),
    url(r'^configuration/host/(?P<host_id>\d+)/delete$', 'core.views.configuration.host_delete', name='host delete'),
    url(r'^configuration/host/(?P<host_id>\d+)/plugins$', 'core.views.configuration.host_plugins', name='host plugins'),

    url(r'^hosttree/group/(?P<group_id>\d+)?$', 'core.views.hosttree.group', name= 'hosttree group'),
    url(r'^hosttree/host/(?P<host_id>\d+)$', 'core.views.hosttree.host', name='hosttree host'),
    url(r'^hosttree/category/(?P<host_id>\d+)$', 'core.views.hosttree.category', name='hosttree category'),

    url(r'^multiviews/', include('multiviews.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'mock_storage' in settings.INSTALLED_APPS:
    urlpatterns = patterns('', url(r'^mock/', include('mock_storage.urls')), *list(urlpatterns))
