"""
Source Form Model.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Data_Source


class Data_Source_Form(forms.ModelForm):
    """
    ``NgModelFormMixin`` & ``ModelForm`` for ``Data_Source``.
    It uses also provide ``get_submit_url`` and ``get_submit_method``.
    """
    class Meta:
        model = Data_Source
        fields = ('name', 'comment',)
        widgets = {
          'name': forms.TextInput({'placeholder': _('Name'), 'class': 'span', 'ng-model': 'tabIndex.form.name'}),
          'comment': forms.Textarea({'placeholder': _('Write a comment about') ,'class': 'span', 'rows': '4', 'ng-model': 'tabIndex.form.comment'}),
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
