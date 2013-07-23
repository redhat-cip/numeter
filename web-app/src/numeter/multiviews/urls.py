from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'multiviews.views.multiviews_index', name='multiviews index'),
    url(r'^get-data/(?P<view_id>\d+)$', 'multiviews.views.get_data', name='view data'),

    # url(r'^plugin/add$', 'multiviews.views.plugin_delete', name='plugin add'),
    # url(r'^plugin/(?P<plugin_id>\d+)$', 'multiviews.views.plugin', name='plugin'),
    # url(r'^plugin/(?P<plugin_id>\d+)/update$', 'multiviews.views.plugin_update', name='plugin update'),
    # url(r'^plugin/(?P<plugin_id>\d+)/delete$', 'multiviews.views.plugin_delete', name='plugin delete'),

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
