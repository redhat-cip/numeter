"""
Group Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Group


class Group_Form(forms.ModelForm):
    """Simple Group Form"""
    class Meta:
        model = Group
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
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
