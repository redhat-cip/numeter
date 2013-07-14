from django.db.models import Field, SubfieldBase, CharField
from django.forms.fields import MultipleChoiceField
from django.conf import settings
from os import listdir, path


class MediaList(list):

    def _make_html_import(self, full_src):
        """Create HTML <script> tag."""
        IMPORT_TEMP = '<script src="%s"></script>'
        return IMPORT_TEMP % full_src

    def _list_available(self):
        return listdir(settings.MEDIA_ROOT+'/graphlib')        

    def _get_full_url(self, src):
        return settings.MEDIA_ROOT+'graphlib/' + src

    def _get_media_url(self, src):
        return settings.MEDIA_URL+'graphlib/' + src

    def _walk(self):
        for f in self:
            full_src = settings.MEDIA_ROOT+'graphlib/'+f
            media_src = settings.MEDIA_URL+'graphlib/'+f
            if not path.exists(full_src):
                print full_src, '---'
                continue
            elif not path.isdir(full_src):
                yield media_src
            # Search in directory
            else:
                for sf in listdir(full_src):
                    if path.exists(full_src+'/'+sf):
                        yield media_src+'/'+sf

    def htmlize(self):
        """
        Return an generator of HTML <script> tag of all of
        files chosen.
        Can search files in one subdirectory.
        """
        return [ self._make_html_import(s) for s in self._walk() ]


class MediaField(CharField):
    """
    Custom Field which saves chosen from MEDIA_ROOT.
    Choices are media files and stored as splited string.
    """
    
    description = "A choice of files in media"
    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2000 # Why not ?
        super(MediaField, self).__init__(*args, **kwargs)
        # choices are MEDIA_ROOT
        self._choices = [ (x,x) for x in listdir(settings.MEDIA_ROOT+'/graphlib') ]

    def to_python(self, value):
        """From VARCHAR to list()."""
        if isinstance(value, basestring):
            return MediaList(value.split())
        elif isinstance(value, (list,tuple)):
            return MediaList(value)

    def validate(self, value, model_instance):
        # TODO : Make validation
        return

    def get_prep_value(self, value):
        """From list() to string."""
        return ' '.join(value)

    def formfield(self, **kwargs):
        """Automaticaly uses MultipleChoiceField."""
        kwargs['choices'] = self.choices
        return MultipleChoiceField(**kwargs)
