from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class Multiview_Manager(models.Manager):
    def user_filter(self, user):
        """Filter multiviews authorized for a given user."""
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(views__sources__plugin__host__group__in=user.groups.all()).distinct()

    def web_filter(self, q):
        """Extended search from a string."""
        views = self.filter(
            Q(name__icontains=q) |
            Q(views__name__icontains=q)
        ).distinct()
        return views

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized multiviews."""
        views = self.web_filter(q)
        if user.is_superuser:
            return views
        return views.filter(views__sources__plugin__host__group__in=user.groups.all()).distinct()


class Multiview(models.Model):
    name = models.CharField(_('name'), max_length=300)
    views = models.ManyToManyField('multiviews.View')
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)

    objects = Multiview_Manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = 'multiview'
        verbose_name_plural = 'multiviews'

    def __unicode__(self):
        return self.name

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

