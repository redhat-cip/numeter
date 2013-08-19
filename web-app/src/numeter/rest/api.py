from tastypie.resources import ModelResource
from core.models import Storage, Host, User, Group
from multiviews.models import Plugin, Data_Source


class StorageResource(ModelResource):
    class Meta:
        queryset = Storage.objects.all()
        resource_name = 'storage'


class HostResource(ModelResource):
    class Meta:
        queryset = Host.objects.all()
        resource_name = 'host'


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'


class GroupResource(ModelResource):
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'


class PluginResource(ModelResource):
    class Meta:
        queryset = Plugin.objects.all()
        resource_name = 'plugin'


class SourceResource(ModelResource):
    class Meta:
        queryset = Data_Source.objects.all()
        resource_name = 'source'
