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
