from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from multiviews.models import Multiview
from rest.resources.models import View_Resource
from rest.authorization import FilteringAuthorization


class Multiview_Resource(ModelResource):
    views = fields.ManyToManyField(View_Resource, 'views')
    class Meta:
        authorization = FilteringAuthorization()
        queryset = Multiview.objects.all()
        resource_name = 'multiview'
        filtering = {
          'name': ALL,
          'views': ALL_WITH_RELATIONS,
        }

