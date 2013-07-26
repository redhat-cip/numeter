from django import forms
from django.utils.translation import ugettext_lazy as _

from multiviews.models import Data_Source, Plugin, View, Multiview, Event


class Data_Source_Form(forms.ModelForm):
    class Meta:
        model = Data_Source
        fields = ('comment',)
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Comment'),'class':'span'}),
        }


class Plugin_Form(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = ('comment',)
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Comment'),'class':'span'}),
        }


class View_Form(forms.ModelForm):
    class Meta:
        model = View
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'sources': forms.SelectMultiple({'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Comment'),'class':'span'}),
        }


class Multiview_Form(forms.ModelForm):
    class Meta:
        model = Multiview
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'views': forms.SelectMultiple({'class':'span'}),
        }


class Event_Form(forms.ModelForm):
    class Meta:
        model = Event
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'source': forms.Select({'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Comment'),'class':'span'}),
            'date': forms.TextInput({'placeholder':_('Date'),'class':'span'}),
        }
