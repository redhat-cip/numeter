# TODO: See what's useless
from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager as _UserManager
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from core.models import Host, Group
from core.models.utils import MediaField


class UserManager(_UserManager):
    """Custom Manager with extra methods."""
    def web_filter(self, q):
        return self.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(groups__name__icontains=q)
        ).distinct()

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        """Base method to create user."""
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
            is_staff=is_staff, is_active=True,
            is_superuser=is_superuser, last_login=now(),
            date_joined=now(), graph_lib='dygraph',
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        """Create simple user."""
        return self._create_user(username, '', password, False, False, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """Create super user."""
        return self._create_user(username, '', password, True, True, **extra_fields)

    def all_superuser(self):
        """Return all superusers."""
        return self.filter(is_superuser=True)

    def all_simpleuser(self):
        """Return all simple users."""
        return self.filter(is_superuser=False)


class User(AbstractBaseUser):
    """Model to deal with authentification."""
    username = models.CharField(_('username'), max_length=30, unique=True)
    email = models.EmailField(_('email address'), blank=True)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), default=now)
    graph_lib = MediaField()
    groups = models.ManyToManyField('core.Group', null=True, blank=True)

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

    def has_perm(*args):
        return True

    def has_module_perms(*args):
        return True

    def has_access(self, obj):
        from core.models import Plugin, Data_Source
        if self.is_superuser and self.is_active:
            return True
        else:
            if isinstance(obj, User):
                return self == obj
            if isinstance(obj, Group):
                return self.groups.filter(pk=obj.pk).exists()
            elif isinstance(obj, Host):
                return self.groups.filter(pk=obj.group.pk).exists()
            elif isinstance(obj, Plugin):
                return self.groups.filter(pk=obj.host.group.pk).exists()
            elif isinstance(obj, Data_Source):
                return self.groups.filter(pk=obj.plugin.host.group.pk).exists()
        return False
