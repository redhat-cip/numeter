from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class UserManager(UserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
            is_staff=is_staff, is_active=True,
            is_superuser=is_superuser, last_login=now(),
            date_joined=now(), **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, '', password, False, False, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, '', password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), default=now)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ()

    class Meta:
        app_label = 'core'
        ordering = ('username',)
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        return self.username

    def get_update_url(self):
        return reverse('update profile', args=[str(self.id)])

    def get_update_password_url(self):
        return reverse('update password', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('delete profile', args=[str(self.id)])

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
