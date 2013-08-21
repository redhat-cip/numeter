from django.conf.urls import url
from tastypie.resources import Resource
from core.models import Storage


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
            url(r"^hinfo$", self.wrap_view('hinfo'), name="api_hinfo"),
            url(r"^list$", self.wrap_view('list'), name="api_list"),
            url(r"^info$", self.wrap_view('info'), name="api_info"),
            url(r"^data$", self.wrap_view('data'), name="api_data"),
        ]

    def hinfo(self, request, *args, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        # Get data
        storage = Storage.objects.which_storage(request.GET['host'])
        data = storage.get_info(request.GET['host'])
        return self.create_response(request, data)

    def list(self, request, *args, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        # Get data
        storage = Storage.objects.which_storage(request.GET['host'])
        data = storage.get_plugins(request.GET['host'])
        return self.create_response(request, data)

    def info(self, request, *args, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        # Get data
        storage = Storage.objects.which_storage(request.GET['host'])
        data = storage.get_plugin_data_sources(request.GET['host'], request.GET['plugin'])
        return self.create_response(request, data)

    def data(self, request, *args, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        # Get data
        storage = Storage.objects.which_storage(request.GET['host'])
        req = {
          'hostid':request.GET['host'],
          'plugin':request.GET['plugin'],
          'ds':request.GET['ds'],
          'res':request.GET['res'],
        }
        data = storage.get_data(**req)
        return self.create_response(request, data)
