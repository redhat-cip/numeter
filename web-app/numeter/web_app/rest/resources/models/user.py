from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from core.models import User
from rest.resources.models import Group_Resource
from rest.authorization import AdminAuthorization


class User_Resource(ModelResource):
    groups = fields.ManyToManyField(Group_Resource, 'groups')
    class Meta:
        authorization = AdminAuthorization()
        queryset = User.objects.all()
        excludes = ['password']
        resource_name = 'user'
        filtering = {
          'name': ALL,
          'groups': ALL_WITH_RELATIONS,
        }

