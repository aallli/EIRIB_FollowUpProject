from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Knowledge Category')
        verbose_name_plural = _('Knowledge Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False)
    category = models.ForeignKey(Category, verbose_name=_('Category'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Knowledge Sub-Category')
        verbose_name_plural = _('Knowledge Sub-Categories')
        ordering = ['category', 'name']
        unique_together = ['name', 'category']

    def __str__(self):
        return '%s: %s' % (self.category, self.name)

    def __unicode__(self):
        return '%s: %s' % (self.category, self.name)


class Activity(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)
    max_score = models.IntegerField(verbose_name=_('Maximum Score'), default=10, blank=False)
    limit = models.IntegerField(verbose_name=_('Limit'), default=1, blank=False)
    limit = models.IntegerField(verbose_name=_('Limit'), default=1, blank=False)

    class Meta:
        verbose_name = _('Knowledge Activity')
        verbose_name_plural = _('Knowledge Activities')
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
