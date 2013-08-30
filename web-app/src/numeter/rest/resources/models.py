from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from core.models import Storage, Host, User, Group, Plugin, Data_Source
from multiviews.models import View, Multiview


class Storage_Resource(ModelResource):
    class Meta:
        queryset = Storage.objects.all()
        resource_name = 'storage'


class Host_Resource(ModelResource):
    class Meta:
        queryset = Host.objects.all()
        resource_name = 'host'
        filtering = {
          'id': ALL,
        }


class User_Resource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'


class Group_Resource(ModelResource):
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'


class Plugin_Resource(ModelResource):
    host = fields.ForeignKey(Host_Resource, 'host')
    class Meta:
        queryset = Plugin.objects.all()
        resource_name = 'plugin'
        filtering = {
          'name': ALL,
          'host': ALL_WITH_RELATIONS,
        }


class Source_Resource(ModelResource):
    class Meta:
        queryset = Data_Source.objects.all()
        resource_name = 'source'


class View_Resource(ModelResource):
    class Meta:
        queryset = View.objects.all()
        resource_name = 'view'


class Multiview_Resource(ModelResource):
    class Meta:
        queryset = Multiview.objects.all()
        resource_name = 'multiview'
