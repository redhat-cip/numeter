from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'multiviews.views.index.multiviews_index', name='multiviews index'),
    url(r'^search$', 'multiviews.views.index.search', name='multiviews search'),
    ## JSON
    url(r'^view/(?P<view_id>\d+)/data$', 'multiviews.views.get_data.view', name='view data'),
    url(r'^source/(?P<source_id>\d+)/data$', 'multiviews.views.get_data.source', name='source data'),
    ## Customize
    url(r'^customize$', 'multiviews.views.customize.index.index', name='multiviews customize index'),
    # Source
    url(r'^customize/source$', 'multiviews.views.customize.source.index', name='multiviews customize source index'),
    url(r'^customize/source/list$', 'multiviews.views.customize.source.list', name='multiviews customize source list'),
    url(r'^customize/source/add$', 'multiviews.views.customize.source.add', name='multiviews customize source add'),
    url(r'^customize/source/(?P<source_id>\d+)$', 'multiviews.views.customize.source.edit', name='multiviews customize source edit'),
    # View
    url(r'^customize/view$', 'multiviews.views.customize.view.index', name='multiviews customize view index'),
    url(r'^customize/view/list$', 'multiviews.views.customize.view.list', name='multiviews customize view list'),
    url(r'^customize/view/add$', 'multiviews.views.customize.view.add', name='multiviews customize view add'),
    url(r'^customize/view/(?P<view_id>\d+)$', 'multiviews.views.customize.view.edit', name='multiviews customize view edit'),
    url(r'^customize/view/(?P<view_id>\d+)/add_source$', 'multiviews.views.customize.view.fast_add_source', name='multiviews customize view fast add source'),
    url(r'^customize/view/(?P<view_id>\d+)/remove_source$', 'multiviews.views.customize.view.fast_remove_source', name='multiviews customize view fast remove source'),
    url(r'^customize/view/fast_add$', 'multiviews.views.customize.view.fast_add', name='multiviews customize view fast add'),
    # Multiview
    url(r'^customize/multiview$', 'multiviews.views.customize.multiview.index', name='multiviews customize multiview index'),
    url(r'^customize/multiview/list$', 'multiviews.views.customize.multiview.list', name='multiviews customize multiview list'),
    url(r'^customize/multiview/add$', 'multiviews.views.customize.multiview.add', name='multiviews customize multiview add'),
    url(r'^customize/multiview/(?P<multiview_id>\d+)$', 'multiviews.views.customize.multiview.edit', name='multiviews customize multiview edit'),
    # Event
    url(r'^customize/event$', 'multiviews.views.customize.event.index', name='multiviews customize event index'),
    url(r'^customize/event/list$', 'multiviews.views.customize.event.list', name='multiviews customize event list'),
    url(r'^customize/event/add$', 'multiviews.views.customize.event.add', name='multiviews customize event add'),
    url(r'^customize/event/(?P<event_id>\d+)$', 'multiviews.views.customize.event.edit', name='multiviews customize event edit'),
)
