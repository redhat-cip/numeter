from django.contrib.auth.models import User
from django import forms


class User_Form(forms.ModelForm):
    class Meta:
        model = User
        widgets = {
            'username': forms.TextInput({'placeholder':'Username'}),
            'email': forms.TextInput({'placeholder':'Email'}),
        }


class User_Admin_EditForm(User_Form):
	class Meta(User_Form.Meta):
		exclude = ('password','last_login','is_staff','date_joined')


class User_EditForm(User_Admin_EditForm):
	class Meta(User_Admin_EditForm.Meta):
		exclude = User_Admin_EditForm.Meta.exclude + ('is_superuser','groups','user_permissions','is_active')
