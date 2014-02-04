"""
View Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from configuration.forms.base import Base_ModelForm
from core.models import Data_Source as Source
from multiviews.models import View


class View_Form(forms.ModelForm):
    """
    ``NgModelFormMixin`` & ``ModelForm`` for ``View``.
    It uses also provide ``get_submit_url`` and ``get_submit_method``.
    """
    class Meta:
        model = View

    def get_submit_url(self):
        """Return url matching with creation or updating."""
        if self.instance.id:
            return self.instance.get_rest_detail_url()
        else:
            return self.instance.get_rest_list_url()

    def get_submit_method(self):
        """Return method matching with creation or updating."""
        if self.instance.id:
            return 'PATCH'
        else:
            return 'POST'


class Extended_View_Form(View_Form):
    """Small View ModelForm."""
    class Meta:
        model = View
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span', 'ng-model': 'tabIndex.form.name'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'2', 'ng-model': 'tabIndex.form.comment'}),
          'warning': forms.TextInput({'placeholder':_('Warning threshold (optional)'),'class':'span', 'ng-model': 'tabIndex.form.warning'}),
          'critical': forms.TextInput({'placeholder':_('Critical threshold (optional)'),'class':'span', 'ng-model': 'tabIndex.form.critical'}),
          'sources': forms.TextInput({'class':'span', 'ui-select2': 'remote_select.sources', 'multiple': '', 'type': 'hidden', 'ng-model': 'tabIndex.form.sources'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Extended_View_Form, self).__init__(*args, **kwargs)
        if not self.user:
            raise TypeError('Object must have a User object for initialization')
        self.fields['sources'].queryset = Source.objects.user_filter(self.user)[:20]
