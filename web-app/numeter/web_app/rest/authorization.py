from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


class AdminAuthorization(Authorization):
    """Only admin can use this Authorization."""
    def read_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return object_list
        raise Unauthorized('Only superuser can access.')

    def read_detail(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True
        raise Unauthorized('Only superuser can access.')

    def create_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True
        raise Unauthorized('Only superuser can access.')

    def create_detail(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True
        raise Unauthorized('Only superuser can access.')

    def update_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True
        raise Unauthorized('Only superuser can access.')

    def update_detail(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True
        raise Unauthorized('Only superuser can access.')

    def delete_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True
        raise Unauthorized('Only superuser can access.')
    
    def delete_detail(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True
        raise Unauthorized('Only superuser can access.')


class FilteringAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.user_filter(bundle.request.user)
