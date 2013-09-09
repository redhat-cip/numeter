from django.forms import ModelForm


class Base_ModelForm(ModelForm):
    """Base ModelForm class with extras method."""
    def method(self):
        """Return appropriate HTML method."""
        if self.instance.id:
            return 'PATCH'
        else:
            return 'POST'
