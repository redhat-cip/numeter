from django.db import models


# http://www.djangosnippets.org/snippets/562/#c673
class QuerySetManager(models.Manager):
    use_for_related_fields = True
    def __init__(self, qs_class=models.query.QuerySet):
        self.queryset_class = qs_class
        super(QuerySetManager, self).__init__()

    def get_query_set(self):
        return self.queryset_class(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args) 

class QuerySet(models.query.QuerySet):
    """Base QuerySet class for adding custom methods that are made
    available on both the manager and subsequent cloned QuerySets"""
    @classmethod
    def as_manager(cls, ManagerClass=QuerySetManager):
        return ManagerClass(cls) 
