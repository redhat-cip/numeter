from django.conf.urls import patterns, url, include
from tastypie.api import Api
from rest.api import StorageResource, HostResource, UserResource, GroupResource, PluginResource, SourceResource

api = Api(api_name='api')
api.register(StorageResource())
api.register(HostResource())
api.register(UserResource())
api.register(GroupResource())
api.register(PluginResource())
api.register(SourceResource())


urlpatterns = patterns('',
  (r'', include(api.urls)),
)
