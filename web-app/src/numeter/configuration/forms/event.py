from django import forms
from django.utils.translation import ugettext_lazy as _
from multiviews.models import Event

class Event_Form(forms.ModelForm):
    class Meta:
        model = Event
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'source': forms.Select({'class':'span'}),
          'start_date': forms.TextInput({'placeholder':_('End date'),'class':'span'}),
          'end_date': forms.TextInput({'placeholder':_('Start date'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }

