from django.conf.urls import patterns, url, include
from tastypie.api import Api
from rest.resources.models import Storage_Resource, Host_Resource, User_Resource, Group_Resource, Plugin_Resource, Source_Resource, View_Resource, Multiview_Resource 
from rest.resources.wild_storage import Wild_Storage_Resource

# Core API
core_api = Api(api_name='api')
core_api.register(Storage_Resource())
core_api.register(Host_Resource())
core_api.register(User_Resource())
core_api.register(Group_Resource())
core_api.register(Plugin_Resource())
core_api.register(Source_Resource())
core_api.register(View_Resource())
core_api.register(Multiview_Resource())

urlpatterns = patterns('',
  (r'', include(core_api.urls)),
  (r'wild_storage/', include(Wild_Storage_Resource().urls)),
)
