from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from multiviews.models import View
from rest.resources.models import Source_Resource
from rest.authorization import FilteringAuthorization


class View_Resource(ModelResource):
    sources = fields.ManyToManyField(Source_Resource, 'sources')
    class Meta:
        authorization = FilteringAuthorization()
        queryset = View.objects.all()
        resource_name = 'view'
        filtering = {
          'name': ALL,
          'sources': ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        bundle.data['fullname'] = bundle.obj.__unicode__()
        return bundle
