from django.conf.urls import url
from django.utils.decorators import available_attrs
from tastypie.resources import Resource
from core.models import Storage
from functools import wraps


def find_storage():
    """Decorator for valid request and get storage from request.GET['host']."""
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, request, *args, **kwargs):
            self.method_check(request, allowed=['get'])
            self.is_authenticated(request)
            self.throttle_check(request)
            self.log_throttled_access(request)

            self.storage = Storage.objects.which_storage(request.GET['host'])
            return func(self, request, *args, **kwargs)
        return inner
    return decorator


class Wild_Storage_Resource(Resource):
    """
    A super Storage API which allow to be requested as a storage
    without know where is the host.
    """
    class Meta:
        resource_name = 'wild_storage'
        allowed_methods = ['get']

    def base_urls(self):
        return [
            url(r"^$", self.wrap_view('index'), name="wild_storage_index"),
            url(r"^hosts$", self.wrap_view('hosts'), name="wild_storage_hosts"),
            url(r"^hinfo$", self.wrap_view('hinfo'), name="wild_storage_hinfo"),
            url(r"^list$", self.wrap_view('list'), name="wild_storage_list"),
            url(r"^info$", self.wrap_view('info'), name="wild_storage_info"),
            url(r"^data$", self.wrap_view('data'), name="wild_storage_data"),
        ]

    def index(self, request, *args, **kwargs):
        # TODO: make index
        data = {}
        return self.create_response(request, data)

    def hosts(self, request, *args, **kwargs):
        data = {}
        [ data.update(s.get_hosts()) for s in Storage.objects.exclude(name__icontains='wild') ]
        return self.create_response(request, data)

    @find_storage()
    def hinfo(self, request, *args, **kwargs):
        data = self.storage.get_info(request.GET['host'])
        return self.create_response(request, data)

    @find_storage()
    def list(self, request, *args, **kwargs):
        data = self.storage._connect('plugins', {'hostid':request.GET['host']})
        return self.create_response(request, data)

    @find_storage()
    def info(self, request, *args, **kwargs):
        data = self.storage.get_plugin_data_sources(request.GET['host'], request.GET['plugin'])
        return self.create_response(request, data)

    @find_storage()
    def data(self, request, *args, **kwargs):
        req = {
          'hostid':request.GET['host'],
          'plugin':request.GET['plugin'],
          'ds':request.GET['ds'],
          'res':request.GET['res'],
        }
        data = self.storage.get_data(**req)
        return self.create_response(request, data)
