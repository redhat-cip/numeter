from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from core.models import Storage, Host, User, Group, Plugin, Data_Source


class StorageResource(ModelResource):
    class Meta:
        queryset = Storage.objects.all()
        resource_name = 'storage'


class HostResource(ModelResource):
    class Meta:
        queryset = Host.objects.all()
        resource_name = 'host'
        filtering = {
          'id': ALL,
        }


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'


class GroupResource(ModelResource):
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'


class PluginResource(ModelResource):
    host = fields.ForeignKey(HostResource, 'host')
    class Meta:
        queryset = Plugin.objects.all()
        resource_name = 'plugin'
        filtering = {
          'name': ALL,
          'host': ALL_WITH_RELATIONS,
        }


class SourceResource(ModelResource):
    class Meta:
        queryset = Data_Source.objects.all()
        resource_name = 'source'
