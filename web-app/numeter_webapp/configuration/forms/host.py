"""
Host Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Host


class Host_Form(forms.ModelForm):
    """Basic Host ModelForm."""
    class Meta:
        model = Host
        widgets = {
            'name': forms.TextInput({'placeholder':_("Host's name"), 'class':'span'}),
            'hostid': forms.TextInput({'placeholder':'ID', 'class':'span'}),
            'storage': forms.Select({'class':'span'}),
            'group': forms.Select({'class':'span'}),
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
