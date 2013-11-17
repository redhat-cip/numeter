from django import forms
from django.utils.translation import ugettext_lazy as _
from multiviews.models import Event

class Event_Form(forms.ModelForm):
    class Meta:
        model = Event
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'short_text': forms.TextInput({'placeholder':_('Text shown on graph'),'class':'span'}),
          'hosts': forms.SelectMultiple({'class':'span', 'size':4}),
          'date': forms.DateTimeInput(format="%Y-%m-%d %H:%M", attrs={'placeholder':_('Date (format: "Y-m-d H:M")'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }

