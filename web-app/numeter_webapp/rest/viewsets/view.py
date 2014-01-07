"""
View ViewSet module.
"""

from rest_framework.viewsets import ModelViewSet 
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST 

from multiviews.models import View
from rest.serializers import ViewSerializer
from rest.permissions import IsOwnerOrForbidden
from rest.views import ModelListDelete


class ViewViewSet(ModelListDelete, ModelViewSet):
    """
    View endpoint, availaible for all users. It filters View by its user and
    groups.
    """
    model = View
    permission_classes = (IsOwnerOrForbidden,)
    serializer_class = ViewSerializer
    allowed_methods = ('POST', 'PATCH', 'DELETE', 'GET')

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        objects = self.model.objects.user_web_filter(q, self.request.user)
        # ID filter
        ids = self.request.QUERY_PARAMS.get('id', [])
        try:
            objects = objects.filter(id__in=ids) if ids else objects
        except ValueError:
            from json import loads
            ids = loads(ids)
            objects = objects.filter(id__in=ids) if ids else objects
        return objects

    # def create(self, request):
    #     """
    #     Base method replaced for automaticaly make users and groups.
    #     """
    #     serializer = ViewSerializer(data=request.DATA)
    #     if serializer.is_valid():
    #         view = serializer.save()
    #         if not view.groups.all().exists():
    #             view.groups.add(*request.user.groups.all())
    #         if request.DATA.get('is_private', False):
    #             view.users.add(request.user)
    #         return Response(JSONRenderer().render(serializer.data),
    #                         status=HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors,
    #                     status=HTTP_400_BAD_REQUEST)
