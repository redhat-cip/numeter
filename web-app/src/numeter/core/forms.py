from django import forms
from django.utils.translation import ugettext_lazy as _

from core.models import User, Storage


class User_Form(forms.ModelForm):
    class Meta:
        model = User
        widgets = {
            'username': forms.TextInput({'placeholder':_('Username')}),
            'email': forms.TextInput({'placeholder':_('Email')}),
        }


class User_Admin_EditForm(User_Form):
    class Meta(User_Form.Meta):
        exclude = ('password','last_login','is_staff','date_joined')


class User_EditForm(User_Admin_EditForm):
    class Meta(User_Form.Meta):
        fields = ('username','email')


class User_PasswordForm(User_Form):
    old = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('Old password')}))
    new_1 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('New password')}))
    new_2 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('Confirmation')}))

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


class Storage_Form(forms.ModelForm):
    class Meta:
        model = Storage
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name')}),
            'address': forms.TextInput({'placeholder':_('Address')}),
            'port': forms.TextInput({'placeholder':_('Port')}),
            'port': forms.TextInput({'placeholder':_('Port')}),
            'url_prefix': forms.TextInput({'placeholder':_('URL prefix')}),
            'login': forms.TextInput({'placeholder':_('Login')}),
            'password': forms.TextInput({'placeholder':_('Password')}),
        }
