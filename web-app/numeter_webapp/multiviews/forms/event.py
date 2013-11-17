from django import forms
from django.utils.translation import ugettext_lazy as _
from configuration.forms.event import Event_Form
from core.models import Host
from multiviews.models import Event


class Small_Event_Form(Event_Form):
    """Small Event ModelForm."""
    available_hosts = forms.ModelMultipleChoiceField(
      queryset = Host.objects.all(),
      widget=forms.SelectMultiple({'class':'span'})
    )
    hosts = forms.ModelMultipleChoiceField(
      queryset = Host.objects.all(),
      widget=forms.SelectMultiple({'class':'span'})
    )

    class Meta:
        model = Event
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'short_text': forms.TextInput({'placeholder':_('Small description'),'class':'span'}),
          'date': forms.DateTimeInput(format="%Y-%m-%d %H:%M", attrs={'placeholder':_('Date (format: "Y-m-d H:M")'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'2'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Small_Event_Form, self).__init__(*args, **kwargs)
        if not self.user:
            raise TypeError('Object must have a User object for initialization')
        if self.instance.id is None:
            self.fields['hosts'].queryset = Host.objects.all()
            self.fields['available_hosts'].queryset = Host.objects.user_filter(self.user)
        else:
            self.fields['hosts'].queryset = self.instance.hosts.all()
            self.fields['available_hosts'].queryset = Host.objects.user_filter(self.user).exclude(pk__in=self.instance.hosts.all())

