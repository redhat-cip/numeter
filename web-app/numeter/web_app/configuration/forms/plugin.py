from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Plugin


class Plugin_Form(forms.ModelForm):
    """Simple Plugin ModelForm."""
    class Meta:
        model = Plugin
        fields = ('comment',)
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }
