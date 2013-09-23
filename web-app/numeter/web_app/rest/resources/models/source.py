from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from core.models import Data_Source
from rest.resources.models import Plugin_Resource
from rest.authorization import FilteringAuthorization


class Source_Resource(ModelResource):
    plugin = fields.ForeignKey(Plugin_Resource, 'plugin')
    class Meta:
        authorization = FilteringAuthorization()
        queryset = Data_Source.objects.all()
        resource_name = 'source'
        filtering = {
          'name': ALL,
          'plugin': ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        bundle.data['host'] = bundle.obj.plugin.host
        bundle.data['fullname'] = bundle.obj.__unicode__()
        return bundle
