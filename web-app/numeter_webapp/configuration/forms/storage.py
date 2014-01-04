"""
Storage Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from djangular.forms.angular_model import NgModelFormMixin
from core.models import Storage


class Storage_Form(NgModelFormMixin, forms.ModelForm):
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

    def __init__(self, *args, **kwargs):
        kwargs['scope_prefix'] = 'form'
        super(Storage_Form, self).__init__(*args, **kwargs)
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
