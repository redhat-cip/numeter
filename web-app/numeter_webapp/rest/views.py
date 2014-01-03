from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from core.models import Host


class ModelListDelete(object):
    """
    Base class for Viewset, must be mixed with a regular.
    It allows to use list view to delete multiple instance.
    It adds a `delete_list` method for perform this action.
    It uses `request.DATA['id']` which is supposed to be a list of id. 
    """
    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '') or self.request.DATA.get('q', '')
        return self.model.objects.user_web_filter(q, self.request.user)

    def delete_list(self, request, *args, **kwargs):
        try:
            queryset = self.model.objects.user_filter(self.request.user).filter(id__in=request.DATA.get('id'))
        except AttributeError:
            queryset = self.model.objects.filter(id__in=request.DATA.get('id'))
        except ValueError:
            return Response(status=HTTP_400_BAD_REQUEST)

        if not queryset.exists():
            return Response(status=HTTP_404_NOT_FOUND)
        queryset.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers # deprecate?
        try:
            self.initial(request, *args, **kwargs)
            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                if request.method == 'DELETE' and \
                        handler == self.http_method_not_allowed:
                    handler = self.delete_list
            else:
                handler = self.http_method_not_allowed,
                self.http_method_not_allowed

            response = handler(request, *args, **kwargs)
        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response
