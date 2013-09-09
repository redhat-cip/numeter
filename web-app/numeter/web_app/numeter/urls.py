from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.views.index', name='index'),
    url(r'^apropos$', 'core.views.views.apropos', name='apropos'),
    url(r'^login$', 'core.views.auth.login', name='login'),
    url(r'^logout$', 'core.views.auth.logout', name='logout'),

    url(r'^get/graph/(?P<host_id>\d+)/(?P<plugin>.+)$', 'core.views.hosttree.get_data', name='plugin'),

    url(r'^hosttree/group/(?P<group_id>\d+)?$', 'core.views.hosttree.group', name= 'hosttree group'),
    url(r'^hosttree/host/(?P<host_id>\d+)$', 'core.views.hosttree.host', name='hosttree host'),
    url(r'^hosttree/category/(?P<host_id>\d+)$', 'core.views.hosttree.category', name='hosttree category'),

    url(r'^multiviews/', include('multiviews.urls')),
    url(r'^configuration/', include('configuration.urls')),
    url(r'^', include('rest.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'mock_storage' in settings.INSTALLED_APPS:
    urlpatterns = patterns('', url(r'^mock/', include('mock_storage.urls')), *list(urlpatterns))
