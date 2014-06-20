"""
User Form module.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import User


class User_Form(forms.ModelForm):
    """
    Base User Form. Subclassed for make custom User Form.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'graph_lib', 'is_superuser', 'groups')
        widgets = {
          'username': forms.TextInput({'placeholder':_('Username'),'class':'span', 'ng-model': 'tabIndex.form.username'}),
          'email': forms.TextInput({'placeholder':_('Email'),'class':'span', 'ng-model': 'tabIndex.form.email'}),
          'password': forms.PasswordInput({'placeholder':_('Password'),'class':'span', 'ng-model': 'tabIndex.form.password'}),
          'graph_lib': forms.Select({'class':'span', 'ng-model': 'tabIndex.form.graph_lib'}),
          'groups': forms.TextInput({'class':'span', 'ui-select2': 'remote_select.groups', 'multiple': '', 'data-model': 'groups', 'ng-model': 'tabIndex.form.groups', 'data-placeholder': _('Search groups')})
        }

    def __init__(self, *args, **kwargs):
        #kwargs['scope_prefix'] = 'tabIndex.form'
        super(User_Form, self).__init__(*args, **kwargs)

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


class User_Admin_EditForm(User_Form):
    """
    Form with sensitive fields.
    """
    class Meta(User_Form.Meta):
        exclude = ('password', 'last_login', 'is_staff' ,'date_joined')

    def __init__(self, *args, **kwargs):
        #kwargs['scope_prefix'] = 'tabIndex.form'
        super(User_Admin_EditForm, self).__init__(*args, **kwargs)



class User_CreationForm(User_Form):
    """
    Form with sensitive fields.
    """
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={
      'placeholder': _('Password'),
      'class': 'span',
      'ng-model': 'tabIndex.form.password'
    }))
    password2 = forms.CharField(label=_('Confirmation'), widget=forms.PasswordInput(attrs={
      'placeholder': _('Confirmation'),
      'class': 'span',
      'ng-model': 'tabIndex.form.password2'
    }))
    class Meta(User_Form.Meta):
        exclude = ('last_login', 'is_staff', 'date_joined', 'is_active')

    def clean_password2(self):
        """Check that the two password entries match."""
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError(_('Password and confirmation are not the same.'))
        return password2

    def save(self, commit=True):
        user = super(User_CreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class User_EditForm(User_Admin_EditForm):
    """
    Form with fewer fields.
    """
    class Meta(User_Form.Meta):
        fields = ('username', 'email', 'graph_lib')


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
