from django.db.models import Field, SubfieldBase, CharField
from django.forms.fields import MultipleChoiceField
from django.conf import settings
from os import listdir


class MediaField(CharField):
    
    description = "A choice of files in media"
    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2000
        super(MediaField, self).__init__(*args, **kwargs)
        self._choices = [ (x,x) for x in listdir(settings.MEDIA_ROOT+'/graphlib') ]

    def to_python(self, value):
        if isinstance(value, basestring):
            return value.split()
        else:
            return value

    def validate(self, value, model_instance):
        # TODO : Make validation
        return

    def get_prep_value(self, value):
        return ' '.join(value)

    def formfield(self, **kwargs):
        kwargs['choices'] = self.choices
        return MultipleChoiceField(**kwargs)
