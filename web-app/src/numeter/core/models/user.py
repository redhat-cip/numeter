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

    def all_superuser(self):
        return self.filter(is_superuser=True)

    def all_simpleuser(self):
        return self.filter(is_superuser=False)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), default=now)
    graph_lib = models.ForeignKey('GraphLib', default=1)

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

    def get_absolute_url(self):
        return reverse('user', args=[str(self.id)])

    def get_add_url(self):
        return reverse('user add')

    def get_update_url(self):
        if not self.id:
            return self.get_add_url()
        return reverse('user update', args=[str(self.id)])

    def get_update_password_url(self):
        return reverse('update password', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('user delete', args=[str(self.id)])

    def get_list_url(self):
        if self.is_superuser:
            return reverse('superuser list')
        return reverse('user list')

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class GraphLib(models.Model):
    """
    Javascript graphic library.
    """
    def _upload_path(self, filename):
        return 'graphlib/%s/%s' % (str(self.pk), filename)

    name = models.CharField(verbose_name=_('name'), max_length=30, unique=True)
    script_file = models.FileField(upload_to=_upload_path,verbose_name=_('file'))
    comment = models.TextField(_('comment'), max_length=1000)
    # TODO : extensions = MultipleFileField

    class Meta:
        app_label = 'core'
        ordering = ('name',)
        verbose_name = _('graph library')
        verbose_name_plural = _('graph librairies')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('graphlib', args=[str(self.id)])

    def get_update_url(self):
        return reverse('update graphlib', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('delete graphlib', args=[str(self.id)])

