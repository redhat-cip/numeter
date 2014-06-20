"""
Plugin Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Plugin


class Plugin_Form(forms.ModelForm):
    """
    ``NgModelFormMixin`` & ``ModelForm`` for ``Plugin``.
    It uses also provide ``get_submit_url`` and ``get_submit_method``.
    """
    class Meta:
        model = Plugin
        fields = ('comment',)
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span', 'ng-model': 'tabIndex.form.name'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4', 'ng-model': 'tabIndex.form.comment'}),
        }

    def get_submit_url(self):
        """Return url matching with updating or nothing."""
        if self.instance.id:
            return self.instance.get_rest_detail_url()
        else:
            return ''

    def get_submit_method(self):
        """Return method matching with updating or nothing."""
        if self.instance.id:
            return 'PATCH'
        else:
            return ''
