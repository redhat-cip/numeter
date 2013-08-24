from django.conf.urls import patterns, url, include
from tastypie.api import Api
from rest.api import StorageResource, HostResource, UserResource, GroupResource, PluginResource, SourceResource
from rest.resources.wild_storage import Wild_Storage_Resource
from rest.resources.view import View_Resource

# Core API
core_api = Api(api_name='api')
core_api.register(StorageResource())
core_api.register(HostResource())
core_api.register(UserResource())
core_api.register(GroupResource())
core_api.register(PluginResource())
core_api.register(SourceResource())
core_api.register(View_Resource())

urlpatterns = patterns('',
  (r'', include(core_api.urls)),
  (r'wild_storage/', include(Wild_Storage_Resource().urls)),
)
