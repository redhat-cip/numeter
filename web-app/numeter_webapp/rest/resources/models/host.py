from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from core.models import Host
from rest.resources.models import Storage_Resource, Group_Resource
from rest.authorization import FilteringAuthorization


class Host_Resource(ModelResource):
    storage = fields.ForeignKey(Storage_Resource, 'storage')
    group = fields.ForeignKey(Group_Resource, 'group', null=True, blank=True)
    class Meta:
        authorization = FilteringAuthorization()
        queryset = Host.objects.all()
        resource_name = 'host'
        filtering = {
          'name': ALL,
          'group': ALL_WITH_RELATIONS,
          'storage': ALL_WITH_RELATIONS,
        }


