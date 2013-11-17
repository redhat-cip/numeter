from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Host
from configuration.forms.base import Base_ModelForm
from multiviews.models import Skeleton, View


class Skeleton_Form(forms.ModelForm):
    """Skeleton ModelForm."""
    class Meta:
        model = Skeleton
        widgets = {
          'name': forms.TextInput({'placeholder':_('Name'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'2'}),
          'plugin_pattern': forms.TextInput({'placeholder':_("Filter by plugin with regex ('.*' for all)"),'class':'span'}),
          'source_pattern': forms.TextInput({'placeholder':_('Filter by source with regex'),'class':'span'}),
        }

        def get_submit_url(self):
            """Get POST or PATCH url."""
            if self.instance.id:
                return '/api/skeleton/%i' % self.instance.id
            return '/api/skeleton'

class Skeleton_To_View_Form(forms.ModelForm):
    search_host = forms.CharField(
      required=False,
      widget=forms.TextInput({
      'placeholder': _('Search for host'),
      'class': 'span q-opt',
      'data-url': '/api/host/',
      'data-into': '#id_available_hosts',
      'data-chosen': '#id_hosts',
    }))
    available_hosts = forms.ModelMultipleChoiceField(
      queryset = Host.objects.none(),
      widget=forms.SelectMultiple({'class':'span'}),
      required=False
    )
    hosts = forms.ModelMultipleChoiceField(
      queryset = Host.objects.all(),
      widget=forms.SelectMultiple({'class':'span','size':'6'})
    )

    class Meta:
        model = View
        exclude = ('warning','critical','sources')
        widgets = {
          'name': forms.TextInput({'placeholder':_('New view name'),'class':'span'}),
          'comment': forms.Textarea({'placeholder':_('Write a comment about'),'class':'span','rows':'2'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.skeleton = kwargs.pop('skeleton', None)
        super(Skeleton_To_View_Form, self).__init__(*args, **kwargs)
        if not self.user:
            raise TypeError('Object must have a User object for initialization')
        if not self.skeleton:
            raise TypeError('Object must have a Skeleton object for initialization')
        # Blank
        if self.instance.id is None and not self.data:
            self.fields['available_hosts'].queryset = Host.objects.user_filter(self.user)[:20]
            self.fields['hosts'].queryset = Host.objects.none()
        # Creating
        elif not self.instance.id and self.data:
            self.fields['hosts'].queryset = Host.objects.user_filter(self.user)


    def save(self):
        hosts = Host.objects.filter(pk__in=self.data.getlist('hosts'))
        return self.skeleton.create_view(name=self.data['name'], hosts=hosts)
