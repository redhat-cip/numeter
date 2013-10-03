from tastypie.resources import ModelResource
from core.models import Storage
from rest.authorization import AdminAuthorization


class Storage_Resource(ModelResource):
    class Meta:
        authorization = AdminAuthorization()
        queryset = Storage.objects.all()
        resource_name = 'storage'
