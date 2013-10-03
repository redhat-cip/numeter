from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import User


class User_Form(forms.ModelForm):
    """
    Base User Form. Subclassed for make custom User Form.
    """
    class Meta:
        model = User
        fields = ('username','email','password','graph_lib','is_superuser','groups')
        widgets = {
          'username': forms.TextInput({'placeholder':_('Username'),'class':'span'}),
          'email': forms.TextInput({'placeholder':_('Email'),'class':'span'}),
          'password': forms.PasswordInput({'placeholder':_('Password'),'class':'span'}),
          'graph_lib': forms.SelectMultiple({'class':'span'}),
          'groups': forms.SelectMultiple({'class':'span'}),
        }


class User_Admin_EditForm(User_Form):
    """
    Form with sensitive fields.
    """
    class Meta(User_Form.Meta):
        exclude = ('password','last_login','is_staff','date_joined')


class User_CreationForm(User_Form):
    """
    Form with sensitive fields.
    """
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={
      'placeholder': _('Password'),
      'class': 'span'
    }))
    password2 = forms.CharField(label=_('Confirmation'), widget=forms.PasswordInput(attrs={
      'placeholder': _('Confirmation'),
      'class': 'span'
    }))
    class Meta(User_Form.Meta):
        exclude = ('last_login','is_staff','date_joined','is_active','password')

    def clean_password2(self):
        """Check that the two password entries match."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Password and confirmation are not the same.'))
        return password2

    def save(self, commit=True):
        user = super(User_CreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class User_EditForm(User_Admin_EditForm):
    """
    Form with fewer fields.
    """
    class Meta(User_Form.Meta):
        fields = ('username','email','graph_lib')


class User_PasswordForm(User_Form):
    """
    Form for change password.
    """
    old = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('Old password'), 'class':'span'}))
    new_1 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('New password'), 'class':'span'}))
    new_2 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('Confirmation'), 'class':'span'}))

    class Meta(User_Form.Meta):
        model = User
        fields = ()
    
    def is_valid(self):
        if not self.instance.check_password(self.data['old']):
            self.errors['old'] = _('Bad old password')
        if self.data['new_1'] != self.data['new_2']:
            self.errors['new'] = _('Password and confirmation are not same')
        if self.errors:
            return False
        return True

    def save(self, *args, **kwargs):
        self.instance.set_password(self.data['new_1'])
        self.instance.save()
        return self.instance
