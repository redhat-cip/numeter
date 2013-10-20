from django import forms
from django.utils.translation import ugettext_lazy as _
from configuration.forms.base import Base_ModelForm
from core.models import Data_Source as Source
from multiviews.models import View

# TODO:
# View_Form with search field
# When have API

class Extended_View_Form(forms.ModelForm):
    """Small View ModelForm."""
    search_source = forms.CharField(
      required=False,
      widget=forms.TextInput({
      'placeholder': _('Search for sources'),
      'class': 'span q-opt',
      'data-url': '/api/source/',
      'data-into': '#id_available_sources',
      'data-chosen': '#id_sources',
    }))
    available_sources = forms.ModelMultipleChoiceField(
      queryset = Source.objects.none(),
      widget=forms.SelectMultiple({'class':'span'}),
      required=False
    )
    sources = forms.ModelMultipleChoiceField(
      queryset = Source.objects.all(),
      widget=forms.SelectMultiple({'class':'span','size':'6'})
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
        super(Extended_View_Form, self).__init__(*args, **kwargs)
        if not self.user:
            raise TypeError('Object must have a User object for initialization')
        # Blank
        if self.instance.id is None and not self.data:
            self.fields['available_sources'].queryset = Source.objects.user_filter(self.user)[:20]
            self.fields['sources'].queryset = Source.objects.none()
        # Created in GET
        elif self.instance.id and not self.data:
            self.fields['available_sources'].queryset = Source.objects.user_filter(self.user).exclude(pk__in=self.instance.sources.all())[:20]
            self.fields['sources'].queryset = self.instance.sources.all()
        # Created in POST
        elif self.instance.id and self.data:
            self.fields['sources'].queryset = Source.objects.all()
        # Creating
        elif not self.instance.id and self.data:
            self.fields['available_sources'].queryset = Source.objects.all()
            self.fields['sources'].queryset = Source.objects.user_filter(self.user)

        def get_submit_url(self):
            """Get POST or PATCH url."""
            if self.instance.id:
                return '/api/source/%i' % self.instance.id
            return '/api/source'
