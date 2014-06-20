"""
Storage Form module.
"""

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
          'name': forms.TextInput({'placeholder':_('Name'), 'class':'span', 'ng-model': 'tabIndex.form.name'}),
          'address': forms.TextInput({'placeholder':_('Address'), 'class':'span', 'ng-model': 'tabIndex.form.address'}),
          'port': forms.TextInput({'placeholder':_('Port'), 'class':'span', 'ng-model': 'tabIndex.form.port'}),
          'protocol': forms.Select({'class':'span', 'ng-model': 'tabIndex.form.protocol'}),
          'url_prefix': forms.TextInput({'placeholder':_('URL prefix'), 'class':'span', 'ng-model': 'tabIndex.form.url_prefix'}),
          'login': forms.TextInput({'placeholder':_('Login'), 'class':'span', 'ng-model': 'tabIndex.form.login'}),
          'password': forms.TextInput({'placeholder':_('Password'), 'class':'span', 'ng-model': 'tabIndex.form.password'}),
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
