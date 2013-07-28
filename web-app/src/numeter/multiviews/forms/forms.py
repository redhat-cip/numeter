from django import forms
from django.utils.translation import ugettext_lazy as _

from multiviews.models import Data_Source, Plugin, View, Multiview, Event
from multiviews.forms.fields import Super_SelectMultiple


class Data_Source_Form(forms.ModelForm):
    class Meta:
        model = Data_Source
        fields = ('comment',)
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }


class Plugin_Form(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = ('comment',)
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }


class View_Form(forms.ModelForm):
    class Meta:
        model = View
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'sources': forms.SelectMultiple({'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }


class Multiview_Form(forms.ModelForm):
    class Meta:
        model = Multiview
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
            'views': forms.SelectMultiple({'class':'span'}),
            'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'4'}),
        }


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
