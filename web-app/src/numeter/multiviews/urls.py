from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'multiviews.views.index.multiviews_index', name='multiviews index'),
    url(r'^get-data/(?P<view_id>\d+)$', 'multiviews.views.index.get_data', name='view data'),
    url(r'^get-data/source/(?P<source_id>\d+)$', 'multiviews.views.index.get_data_source_data', name='source data'),

    url(r'^conf/plugin$', 'multiviews.views.conf.plugin.index', name='plugin index'),
    url(r'^conf/plugin/list$', 'multiviews.views.conf.plugin.list', name='plugin list'),
    url(r'^conf/plugin/create$', 'multiviews.views.conf.plugin.create_from_host', name='plugin create'),
    url(r'^conf/plugin/(?P<plugin_id>\d+)$', 'multiviews.views.conf.plugin.get', name='plugin'),
    url(r'^conf/plugin/(?P<plugin_id>\d+)/update$', 'multiviews.views.conf.plugin.update', name='plugin update'),
    url(r'^conf/plugin/(?P<plugin_id>\d+)/delete$', 'multiviews.views.conf.plugin.delete', name='plugin delete'),
    url(r'^conf/plugin/(?P<plugin_id>\d+)/create_sources$', 'multiviews.views.conf.plugin.create_sources', name='plugin create sources'),

    url(r'^conf/source/list$', 'multiviews.views.conf.source.list', name='source list'),
    url(r'^conf/source/(?P<source_id>\d+)$', 'multiviews.views.conf.source.get', name='source'),
    url(r'^conf/source/(?P<source_id>\d+)/update$', 'multiviews.views.conf.source.update', name='source update'),
    url(r'^conf/source/(?P<source_id>\d+)/delete$', 'multiviews.views.conf.source.delete', name='source delete'),

    url(r'^conf/view$', 'multiviews.views.conf.view.index', name='view index'),
    url(r'^conf/view/list$', 'multiviews.views.conf.view.list', name='view list'),
    url(r'^conf/view/add$', 'multiviews.views.conf.view.add', name='view add'),
    url(r'^conf/view/(?P<view_id>\d+)$', 'multiviews.views.conf.view.get', name='view'),
    url(r'^conf/view/(?P<view_id>\d+)/update$', 'multiviews.views.conf.view.update', name='view update'),
    url(r'^conf/view/(?P<view_id>\d+)/delete$', 'multiviews.views.conf.view.delete', name='view delete'),

    url(r'^conf/multiview/list$', 'multiviews.views.conf.multiview.list', name='multiview list'),
    url(r'^conf/multiview/add$', 'multiviews.views.conf.multiview.add', name='multiview add'),
    url(r'^conf/multiview/(?P<multiview_id>\d+)$', 'multiviews.views.conf.multiview.get', name='multiview'),
    url(r'^conf/multiview/(?P<multiview_id>\d+)/update$', 'multiviews.views.conf.multiview.update', name='multiview update'),
    url(r'^conf/multiview/(?P<multiview_id>\d+)/delete$', 'multiviews.views.conf.multiview.delete', name='multiview delete'),

    # url(r'^event/add$', 'multiviews.views.event_delete', name='event add'),
    # url(r'^event/(?P<event_id>\d+)$', 'multiviews.views.event', name='event'),
    # url(r'^event/(?P<event_id>\d+)/update$', 'multiviews.views.event_update', name='event update'),
    # url(r'^event/(?P<event_id>\d+)/delete$', 'multiviews.views.event_delete', name='event delete'),
)
