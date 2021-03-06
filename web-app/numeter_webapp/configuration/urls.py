"""
configuration urls module.
"""

# TODO: Use REST API
from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'configuration.views.index.index', name='configuration'),
    # Users
    url(r'^user/add$', 'configuration.views.user.add', name='user add'),
    url(r'^user/(?P<user_id>\d+)$', 'configuration.views.user.get', name='user'),
    # Groups
    url(r'^group/add$', 'configuration.views.group.add', name='group add'),
    url(r'^group/(?P<group_id>\d+)$', 'configuration.views.group.get', name='group'),
    # Storages
    url(r'^storage/add$', 'configuration.views.storage.add', name='storage add'),
    url(r'^storage/(?P<storage_id>\d+)$', 'configuration.views.storage.get', name='storage'),
    url(r'^storage/(?P<storage_id>\d+)/create_hosts$', 'configuration.views.storage.create_hosts', name='storage create hosts'),
    url(r'^storage/bad_hosts$', 'configuration.views.storage.bad_hosts', name='storage bad hosts'),
    # Hosts
    url(r'^host/(?P<host_id>\d+)$', 'configuration.views.host.get', name='host'),
    url(r'^host/(?P<host_id>\d+)/plugins$', 'configuration.views.host.plugins', name='host plugins'),
    # Plugin
    url(r'^plugin$', 'configuration.views.plugin.index', name='plugin index'),
    url(r'^plugin/list$', 'configuration.views.plugin.list', name='plugin list'),
    url(r'^plugin/list/delete$', 'configuration.views.plugin.bulk_delete', name='plugin bulk delete'),
    url(r'^plugin/create$', 'configuration.views.plugin.create_from_host', name='plugin create'),
    url(r'^plugin/(?P<plugin_id>\d+)$', 'configuration.views.plugin.get', name='plugin'),
    url(r'^plugin/(?P<plugin_id>\d+)/update$', 'configuration.views.plugin.update', name='plugin update'),
    url(r'^plugin/(?P<plugin_id>\d+)/create_sources$', 'configuration.views.plugin.create_sources', name='plugin create sources'),
    # Source
    url(r'^source/list$', 'configuration.views.source.list', name='source list'),
    url(r'^source/list/delete$', 'configuration.views.source.bulk_delete', name='source bulk delete'),
    url(r'^source/(?P<source_id>\d+)$', 'configuration.views.source.get', name='source'),
    url(r'^source/(?P<source_id>\d+)/update$', 'configuration.views.source.update', name='source update'),
    url(r'^source/(?P<source_id>\d+)/delete$', 'configuration.views.source.delete', name='source delete'),
    # View
    url(r'^view$', 'configuration.views.view.index', name='view index'),
    url(r'^view/list$', 'configuration.views.view.list', name='view list'),
    url(r'^view/list/delete$', 'configuration.views.view.bulk_delete', name='view bulk delete'),
    url(r'^view/add$', 'configuration.views.view.add', name='view add'),
    url(r'^view/(?P<view_id>\d+)$', 'configuration.views.view.get', name='view'),
    url(r'^view/(?P<view_id>\d+)/update$', 'configuration.views.view.update', name='view update'),
    url(r'^view/(?P<view_id>\d+)/delete$', 'configuration.views.view.delete', name='view delete'),
    url(r'^view/add_sources$', 'configuration.views.view.add_sources', name='view add sources'),
    # Multiview
    url(r'^multiview/list$', 'configuration.views.multiview.list', name='multiview list'),
    url(r'^multiview/list/delete$', 'configuration.views.multiview.bulk_delete', name='multiview bulk delete'),
    url(r'^multiview/add$', 'configuration.views.multiview.add', name='multiview add'),
    url(r'^multiview/(?P<multiview_id>\d+)$', 'configuration.views.multiview.get', name='multiview'),
    url(r'^multiview/(?P<multiview_id>\d+)/update$', 'configuration.views.multiview.update', name='multiview update'),
    url(r'^multiview/(?P<multiview_id>\d+)/delete$', 'configuration.views.multiview.delete', name='multiview delete'),
    # Skeleton
    url(r'^skeleton/list$', 'configuration.views.skeleton.list', name='skeleton list'),
    url(r'^skeleton/list/delete$', 'configuration.views.skeleton.bulk_delete', name='skeleton bulk delete'),
    url(r'^skeleton/add$', 'configuration.views.skeleton.add', name='skeleton add'),
    url(r'^skeleton/(?P<skeleton_id>\d+)$', 'configuration.views.skeleton.get', name='skeleton'),
    url(r'^skeleton/(?P<skeleton_id>\d+)/update$', 'configuration.views.skeleton.update', name='skeleton update'),
    url(r'^skeleton/(?P<skeleton_id>\d+)/delete$', 'configuration.views.skeleton.delete', name='skeleton delete'),
    url(r'^skeleton/(?P<skeleton_id>\d+)/use$', 'configuration.views.skeleton.use', name='skeleton use'),
    # Event
    url(r'^event/list$', 'configuration.views.event.list', name='event list'),
    url(r'^event/list/delete$', 'configuration.views.event.bulk_delete', name='event bulk delete'),
    url(r'^event/add$', 'configuration.views.event.add', name='event add'),
    url(r'^event/(?P<event_id>\d+)$', 'configuration.views.event.get', name='event'),
    url(r'^event/(?P<event_id>\d+)/update$', 'configuration.views.event.update', name='event update'),
    url(r'^event/(?P<event_id>\d+)/delete$', 'configuration.views.event.delete', name='event delete'),
)
