from django import forms
from django.utils.translation import ugettext_lazy as _

from multiviews.models import Plugin, Multiview, Event


class Plugin_Form(forms.ModelForm):
    class Meta:
        model = Plugin
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'host': forms.Select({'class':'span'}),
        }


class Multiview_Form(forms.ModelForm):
    class Meta:
        model = Multiview
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'plugins': forms.SelectMultiple({'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Comment'),'class':'span'}),
        }


class Event_Form(forms.ModelForm):
    class Meta:
        model = Event
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'plugin': forms.Select({'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Comment'),'class':'span'}),
            'date': forms.TextInput({'placeholder':_('Date'),'class':'span'}),
        }
