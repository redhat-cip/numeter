from django import forms
from django.utils.translation import ugettext_lazy as _
from configuration.forms.multiview import Multiview_Form
from multiviews.models import View, Multiview


class Small_Multiview_Form(Multiview_Form):
    """Small Multiview ModelForm."""
    available_views = forms.ModelMultipleChoiceField(
      queryset = View.objects.none(),
      widget=forms.SelectMultiple({'class':'span'})
    )
    views = forms.ModelMultipleChoiceField(
      queryset = View.objects.none(),
      widget=forms.SelectMultiple({'class':'span'})
    )

    class Meta:
        model = Multiview
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'2'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Small_Multiview_Form, self).__init__(*args, **kwargs)
        if not self.user:
            raise TypeError('Object must have a User object for initialization')
        if self.instance.id is None:
            self.fields['views'].queryset = View.objects.none()
            self.fields['available_views'].queryset = View.objects.user_filter(self.user)[:20]
        else:
            self.fields['views'].queryset = self.instance.views.all()
            self.fields['available_views'].queryset = View.objects.user_filter(self.user).exclude(pk__in=self.instance.views.all())[:20]

