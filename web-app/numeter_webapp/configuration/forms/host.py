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
            'name': forms.TextInput({'placeholder':_("Host's name"), 'class':'span', 'ng-model': 'tabIndex.form.name'}),
            'hostid': forms.TextInput({'placeholder':'ID', 'class':'span', 'ng-model': 'tabIndex.form.hostid'}),
            'storage': forms.Select({'class':'span', 'ng-model': 'tabIndex.form.storage'}),
            'group': forms.Select({'class':'span', 'ng-model': 'tabIndex.form.group'}),
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
