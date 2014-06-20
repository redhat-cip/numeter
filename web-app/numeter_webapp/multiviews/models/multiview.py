from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core.models.utils import QuerySet


class Multiview_QuerySetManager(QuerySet):
    def user_filter(self, user):
        """Filter multiviews authorized for a given user."""
        if user.is_superuser:
            return self.all()
        return self.filter(
            Q(users__in=[user]) |
            Q(groups__in=user.groups.all())
        ).distinct()

    def web_filter(self, q):
        """Extended search from a string."""
        return self.filter(
            Q(name__icontains=q) |
            Q(views__name__icontains=q)
        ).distinct()

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized multiviews."""
        multiviews = self.web_filter(q)
        if user.is_superuser:
            return multiviews
        return multiviews.user_filter(user)


class Multiview(models.Model):
    name = models.CharField(_('name'), max_length=300)
    views = models.ManyToManyField('multiviews.View')
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)
    users = models.ManyToManyField('core.User', null=True, blank=True)
    groups = models.ManyToManyField('core.Group', null=True, blank=True)

    objects = Multiview_QuerySetManager.as_manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = 'multiview'
        verbose_name_plural = 'multiviews'

    def __unicode__(self):
        return self.name

    def user_has_perm(self, user):
        """
        Return if a user is allowed to access an instance.
        A user is allowed if super or in same group's group or owned by him.
        """
        if user.is_superuser:
            return True
        return user in self.users.all() or bool( set(user.groups.all()) & set(self.groups.all()) )

    def get_absolute_url(self):
        return reverse('multiview', args=[self.id])

    def get_add_url(self):
        return reverse('multiview add')

    def get_update_url(self):
        if not self.id:
            return reverse('multiview add')
        return reverse('multiview update', args=[self.id])

    def get_delete_url(self):
        return reverse('multiview delete', args=[self.id])

    def get_list_url(self):
        return reverse('multiview list')

    def get_customize_edit_url(self):
        return reverse('multiviews customize multiview edit', args=[self.id])

    def get_rest_list_url(self):
       return reverse('multiview-list') 

    def get_rest_detail_url(self):
       return reverse('multiview-detail', args=[self.id]) 
