from django import forms
from django.utils.translation import ugettext_lazy as _
from multiviews.models import Multiview


class Multiview_Form(forms.ModelForm):
    """Simple Multiview ModelForm."""
    class Meta:
        model = Multiview
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'views': forms.SelectMultiple({'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }

