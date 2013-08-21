from django.conf.urls import patterns, url, include
from tastypie.api import Api
from rest.api import StorageResource, HostResource, UserResource, GroupResource, PluginResource, SourceResource
from rest.resources.wild_storage import Wild_Storage_Resource

# Models API
model_api = Api(api_name='api')
model_api.register(StorageResource())
model_api.register(HostResource())
model_api.register(UserResource())
model_api.register(GroupResource())
model_api.register(PluginResource())
model_api.register(SourceResource())
# Wild Storage API
wild_storage_api = Api(api_name='wild_storage')
wild_storage_api.register(Wild_Storage_Resource())


urlpatterns = patterns('',
  (r'', include(model_api.urls)),
  (r'', include(wild_storage_api.urls)),
)
