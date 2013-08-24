from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Data_Source


class Data_Source_Form(forms.ModelForm):
    class Meta:
        model = Data_Source
        fields = ('comment',)
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }
