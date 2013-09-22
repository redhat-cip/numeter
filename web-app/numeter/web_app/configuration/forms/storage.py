from django import forms
from django.utils.translation import ugettext_lazy as _

from core.models import Storage


class Storage_Form(forms.ModelForm):
    """
    Basic Storage ModelForm.
    """
    class Meta:
        model = Storage
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'), 'class':'span'}),
          'address': forms.TextInput({'placeholder':_('Address'), 'class':'span'}),
          'port': forms.TextInput({'placeholder':_('Port'), 'class':'span'}),
          'protocol': forms.Select({'class':'span'}),
          'url_prefix': forms.TextInput({'placeholder':_('URL prefix'), 'class':'span'}),
          'login': forms.TextInput({'placeholder':_('Login'), 'class':'span'}),
          'password': forms.TextInput({'placeholder':_('Password'), 'class':'span'}),
        }

