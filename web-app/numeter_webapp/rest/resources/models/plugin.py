from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from core.models import Plugin
from rest.resources.models import Host_Resource
from rest.authorization import FilteringAuthorization


class Plugin_Resource(ModelResource):
    host = fields.ForeignKey(Host_Resource, 'host')
    class Meta:
        authorization = FilteringAuthorization()
        queryset = Plugin.objects.all()
        resource_name = 'plugin'
        filtering = {
          'name': ALL,
          'host': ALL_WITH_RELATIONS,
        }

