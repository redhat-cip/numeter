from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core.models.utils import QuerySet
from multiviews.models import View
from hashlib import md5
from re import compile as r_compile


class Skeleton_QuerySetManager(QuerySet):
    def user_filter(self, user):
        """No-op user filter."""
        return self.all()

    def web_filter(self, q):
        """Extended search from a string."""
        return self.filter(
            Q(name__icontains=q) |
            Q(plugin_pattern__icontains=q) |
            Q(source_pattern__icontains=q)
        ).distinct()

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized views."""
        views = self.web_filter(q)
        if user.is_superuser:
            return views


class Skeleton(models.Model):
    """
    Made for create fastly a view.
    Firsly create a ``Skeleton`` with a two regex: plugin and source.
    After, use ``create_view`` method with a list of hosts and it will
    create a view with sources matching.
    """
    name = models.CharField(_('name'), max_length=300, unique=True)
    plugin_pattern = models.CharField(_('plugin pattern'), max_length=100)
    source_pattern = models.CharField(_('source pattern'), max_length=100)
    comment = models.TextField(_('Comment'), max_length=3000, null=True, blank=True)

    objects = Skeleton_QuerySetManager.as_manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = 'skeleton'
        verbose_name_plural = 'skeleton'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('skeleton', args=[self.id])

    def get_add_url(self):
        return reverse('skeleton add')

    def get_update_url(self):
        if not self.id:
            return reverse('skeleton add')
        return reverse('skeleton update', args=[self.id])

    def get_delete_url(self):
        return reverse('skeleton delete', args=[self.id])

    def get_list_url(self):
        return reverse('skeleton list')

    def get_use_url(self):
        return reverse('skeleton use', args=[self.id])

    def create_view(self, name, hosts):
        """Create a view with ``hosts``, skeleton plugin and source patterns."""
        PLUGIN_REG = r_compile(self.plugin_pattern)
        SOURCE_REG = r_compile(self.source_pattern)
        view_sources = []
        for h in hosts:
            plugins = [ p for p in h.get_plugin_list() if PLUGIN_REG.search(p) ]
            plugins = h.create_plugins(plugins)
            for p in plugins:
                sources = [ s for s in p.get_data_sources() if SOURCE_REG.search(s) ]
                sources = p.create_data_sources(sources)
                view_sources.extend(sources)

        view = View.objects.create(name=name)
        view.sources.add(*view_sources)
        return view
