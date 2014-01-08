from django.db import models
from django.db.models import SubfieldBase, CharField
from django.forms.fields import ChoiceField
from django.conf import settings as s
from os import listdir, path


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
    """
    Base QuerySet class for adding custom methods that are made
    available on both the manager and subsequent cloned QuerySets.
    """
    @classmethod
    def as_manager(cls, ManagerClass=QuerySetManager):
        return ManagerClass(cls) 


class MediaList(unicode):
    """
    Object to mmanipulate graphic javascript library.
    Based on ``unicode`` to make a CHARFIELD and save directory name in db.
    """
    def __init__(self, lib):
        super(MediaList, self).__init__(lib)
        self.dir = s.MEDIA_ROOT+'graphlib/'
        self.lib = lib

    def _walk(self):
        """
        Walk on chosen files and return a generator of chosen files.
        """
        # TODO: Make it with os.walk()
        full_src = self.dir + self.lib
        media_src = s.MEDIA_URL+'graphlib/' + self.lib
        # Search in directory
        for subfile_name in listdir(full_src):
            sf = full_src + '/' + subfile_name
            if not path.isfile(sf):
                continue
            elif path.exists(sf):
                yield media_src + '/' + subfile_name

    def get_js(self):
        sources = [ s for s in self._walk() if s.endswith('.js') ]
        sources.sort()
        return sources

    def get_css(self):
        print [ s for s in self._walk() if s.endswith('.css')]
        return [ s for s in self._walk() if s.endswith('.css')]


class MediaField(CharField):
    """
    Custom Field which saves chosen from MEDIA_ROOT.
    Choices are media files and stored as splited string.
    """
    
    description = "A choice of graphic plugin library."
    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2000 # Why not ?
        super(MediaField, self).__init__(*args, **kwargs)
        # choices are MEDIA_ROOT
        self._choices = [ (x, x) for x in listdir(s.MEDIA_ROOT+'graphlib') ]

    def to_python(self, value):
        """Return object to handle it."""
        return MediaList(value)

    def validate(self, value, model_instance):
        # TODO : Make validation
        return

    def get_prep_value(self, value):
        """Save lib name in db."""
        return value.lib

    def formfield(self, **kwargs):
        """Automaticaly uses ChoiceField."""
        kwargs['choices'] = self.choices
        return ChoiceField(**kwargs)
