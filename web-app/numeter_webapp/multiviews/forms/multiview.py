from django import forms
from django.utils.translation import ugettext_lazy as _
from configuration.forms.multiview import Multiview_Form
from multiviews.models import View, Multiview


class Small_Multiview_Form(Multiview_Form):
    """Small Multiview ModelForm."""
    search_view = forms.CharField(
      required=False,
      widget=forms.TextInput({
      'placeholder': _('Search for view'),
      'class': 'span q-opt',
      'data-url': '/api/view/',
      'data-into': '#id_available_views',
      'data-chosen': '#id_views',
    }))
    available_views = forms.ModelMultipleChoiceField(
      queryset = View.objects.none(),
      widget=forms.SelectMultiple({'class':'span'}),
      required=False
    )
    views = forms.ModelMultipleChoiceField(
      queryset = View.objects.none(),
      widget=forms.SelectMultiple({'class':'span','size':'6'})
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
        # Blank
        if self.instance.id is None and not self.data:
            self.fields['available_views'].queryset = View.objects.user_filter(self.user)[:20]
            self.fields['views'].queryset = View.objects.none()
        # Created in GET
        elif self.instance.id and not self.data:
            self.fields['available_views'].queryset = View.objects.user_filter(self.user).exclude(pk__in=self.instance.views.all())[:20]
            self.fields['views'].queryset = self.instance.views.all()
        # Created in POST
        elif self.instance.id and self.data:
            self.fields['views'].queryset = View.objects.all()
        # Creating
        elif not self.instance.id and self.data:
            self.fields['available_views'].queryset = View.objects.all()
            self.fields['views'].queryset = View.objects.user_filter(self.user)
