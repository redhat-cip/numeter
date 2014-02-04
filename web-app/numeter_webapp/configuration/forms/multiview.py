"""
Multiview Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from multiviews.models import View, Multiview


class Multiview_Form(forms.ModelForm):
    """
    ``NgModelFormMixin`` & ``ModelForm`` for ``Multiview``.
    It uses also provide ``get_submit_url`` and ``get_submit_method``.
    """
    class Meta:
        model = Multiview
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span', 'ng-model': 'tabIndex.form.name'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'2', 'ng-model': 'tabIndex.form.comment'}),
          'views': forms.TextInput({'class':'span', 'ui-select2': 'remote_select.views', 'multiple': '', 'type': 'hidden', 'ng-model': 'tabIndex.form.views'}),
        }

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


class Extended_Multiview_Form(Multiview_Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Extended_Multiview_Form, self).__init__(*args, **kwargs)
