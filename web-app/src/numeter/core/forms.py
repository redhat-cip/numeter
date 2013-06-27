from django.contrib.auth.models import User
from django.forms import ModelForm


class User_Form(ModelForm):
    class Meta:
        model = User
