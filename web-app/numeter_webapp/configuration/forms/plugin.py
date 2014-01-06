"""
Plugin Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from djangular.forms.angular_model import NgModelFormMixin
from core.models import Plugin


class Plugin_Form(NgModelFormMixin, forms.ModelForm):
    """
    ``NgModelFormMixin`` & ``ModelForm`` for ``Plugin``.
    It uses also provide ``get_submit_url`` and ``get_submit_method``.
    """
    class Meta:
        model = Plugin
        fields = ('comment',)
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs['scope_prefix'] = 'tabIndex.form'
        super(Plugin_Form, self).__init__(*args, **kwargs)

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
