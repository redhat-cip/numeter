"""
View Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from djangular.forms.angular_model import NgModelFormMixin

from configuration.forms.base import Base_ModelForm
from core.models import Data_Source as Source
from multiviews.models import View


class View_Form(NgModelFormMixin, forms.ModelForm):
    """
    ``NgModelFormMixin`` & ``ModelForm`` for ``View``.
    It uses also provide ``get_submit_url`` and ``get_submit_method``.
    """
    class Meta:
        model = View

    def __init__(self, *args, **kwargs):
        kwargs['scope_prefix'] = 'form'
        super(View_Form, self).__init__(*args, **kwargs)

    def get_submit_url(self):
        """Return url matching with creation or updating."""
        if self.instance.id:
            return self.instance.get_rest_detail_url()
        else:
            return self.instance.get_rest_list_url()

    def get_submit_method(self):
        """Return method matching with creation or updating."""
        if self.instance.id:
            return 'PATCH'
        else:
            return 'POST'


class Extended_View_Form(View_Form):
    """Small View ModelForm."""
    #is_private = forms.BooleanField()
    search_source = forms.CharField(
      required=False,
      widget=forms.TextInput({
      'placeholder': _('Search for sources'),
      'class': 'span q-opt',
      'data-url': '/rest/sources/', #reverse('source-list'),
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
