from django import forms
from django.utils.translation import ugettext_lazy as _
from configuration.forms.view import View_Form
from core.models import Data_Source
from multiviews.models import View


class Small_View_Form(View_Form):
    """Small View ModelForm."""
    available_sources = forms.ModelMultipleChoiceField(
      queryset = Data_Source.objects.all(),
      widget=forms.SelectMultiple({'class':'span'})
    )
    sources = forms.ModelMultipleChoiceField(
      queryset = Data_Source.objects.all(),
      widget=forms.SelectMultiple({'class':'span'})
    )

    class Meta:
        model = View
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'2'}),
          'warning': forms.TextInput({'placeholder':_('Warning threshold (optional)'),'class':'span'}),
          'critical': forms.TextInput({'placeholder':_('Critical threshold (optional)'),'class':'span'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Small_View_Form, self).__init__(*args, **kwargs)
        if not self.user:
            raise TypeError('Object must have a User object for initialization')
        if self.instance.id is None:
            self.fields['sources'].queryset = Data_Source.objects.all()
            self.fields['available_sources'].queryset = Data_Source.objects.user_filter(self.user)
        else:
            self.fields['sources'].queryset = self.instance.sources.all()
            self.fields['available_sources'].queryset = Data_Source.objects.user_filter(self.user).exclude(pk__in=self.instance.sources.all())
