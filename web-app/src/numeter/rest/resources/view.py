from tastypie.resources import ModelResource
from multiviews.models import View


class View_Resource(ModelResource):
    class Meta:
        queryset = View.objects.all()
        resource_name = 'view'
