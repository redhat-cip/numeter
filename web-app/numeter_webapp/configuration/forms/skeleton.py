from django import forms
from django.utils.translation import ugettext_lazy as _
from configuration.forms.base import Base_ModelForm
from multiviews.models import Skeleton

# TODO:
# View_Form with search field
# When have API

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
