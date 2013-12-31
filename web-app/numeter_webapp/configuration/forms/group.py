"""
Group Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from djangular.forms.angular_model import NgModelFormMixin
from core.models import Group


class Group_Form(NgModelFormMixin, forms.ModelForm):
    """Simple Group Form"""
    class Meta:
        model = Group
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs['scope_prefix'] = 'form'
        super(Group_Form, self).__init__(*args, **kwargs)

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
