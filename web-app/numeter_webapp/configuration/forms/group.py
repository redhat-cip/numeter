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

