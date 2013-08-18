from django import forms
from django.utils.translation import ugettext_lazy as _
from multiviews.models import View


class View_Form(forms.ModelForm):
    """Simple View ModelForm."""
    class Meta:
        model = View
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'sources': forms.SelectMultiple({'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
          'warning': forms.TextInput({'placeholder':_('Warning threshold (optional)'),'class':'span'}),
          'critical': forms.TextInput({'placeholder':_('Critical threshold (optional)'),'class':'span'}),
        }

# TODO:
# View_Form with search field
# When have API
