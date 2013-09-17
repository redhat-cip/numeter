from tastypie.resources import ModelResource
from core.models import Group
from rest.authorization import AdminAuthorization


class Group_Resource(ModelResource):
    class Meta:
        authorization = AdminAuthorization()
        queryset = Group.objects.all()
        resource_name = 'group'

