"""
Source Form Model.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Data_Source


class Data_Source_Form(forms.ModelForm):
    class Meta:
        model = Data_Source
        fields = ('name','comment',)
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }

    def get_submit_url(self):
        """Return url matching with creation or updating."""
        if self.instance.id:
            return self.instance.get_rest_detail_url()
        else:
            return ''

    def get_submit_method(self):
        """Return method matching with creation or updating."""
        if self.instance.id:
            return 'PATCH'
        else:
            return ''
