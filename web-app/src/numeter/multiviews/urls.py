from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'multiviews.views.index.multiviews_index', name='multiviews index'),
    url(r'^get-data/(?P<view_id>\d+)$', 'multiviews.views.index.get_data', name='view data'),

    url(r'^conf/plugin$', 'multiviews.views.conf.plugin.index', name='plugin index'),
    url(r'^conf/plugin/list$', 'multiviews.views.conf.plugin.list', name='plugin list'),
    url(r'^conf/plugin/create$', 'multiviews.views.conf.plugin.create_from_host', name='plugin create'),
    url(r'^conf/plugin/(?P<plugin_id>\d+)$', 'multiviews.views.conf.plugin.get', name='plugin'),
    url(r'^conf/plugin/(?P<plugin_id>\d+)/delete$', 'multiviews.views.conf.plugin.delete', name='plugin delete'),
    url(r'^conf/plugin/(?P<plugin_id>\d+)/create_sources$', 'multiviews.views.conf.plugin.create_sources', name='plugin create sources'),

    url(r'^conf/source/list$', 'multiviews.views.conf.source.list', name='source list'),
    url(r'^conf/source/(?P<source_id>\d+)$', 'multiviews.views.conf.source.get', name='source'),
    url(r'^conf/source/(?P<source_id>\d+)/update$', 'multiviews.views.conf.source.update', name='source update'),
    url(r'^conf/source/(?P<source_id>\d+)/delete$', 'multiviews.views.conf.source.delete', name='source delete'),
    # url(r'^multiview/add$', 'multiviews.views.multiview_delete', name='multiview add'),
    # url(r'^multiview/(?P<multiview_id>\d+)$', 'multiviews.views.multiview', name='multiview'),
    # url(r'^multiview/(?P<multiview_id>\d+)/update$', 'multiviews.views.multiview_update', name='multiview update'),
    # url(r'^multiview/(?P<multiview_id>\d+)/delete$', 'multiviews.views.multiview_delete', name='multiview delete'),
    # 
    # url(r'^event/add$', 'multiviews.views.event_delete', name='event add'),
    # url(r'^event/(?P<event_id>\d+)$', 'multiviews.views.event', name='event'),
    # url(r'^event/(?P<event_id>\d+)/update$', 'multiviews.views.event_update', name='event update'),
    # url(r'^event/(?P<event_id>\d+)/delete$', 'multiviews.views.event_delete', name='event delete'),
)
