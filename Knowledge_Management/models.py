from django.db import models
from EIRIB_FollowUp.models import User
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


class CommitteeMember(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'), on_delete=models.CASCADE, unique=True)
    chairman = models.BooleanField(verbose_name=_('Chairman'), default=False)

    class Meta:
        verbose_name = _('Committee Member')
        verbose_name_plural = _('Committee Members')

    def __str__(self):
        return self.user.get_full_name()

    def __unicode__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        if self.chairman:
            for cm in CommitteeMember.objects.all():
                if cm.pk != self.pk:
                    cm.chairman = False
                    cm.save()
        return super(CommitteeMember, self).save(*args, **kwargs)


class Indicator(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Indicator')
        verbose_name_plural = _('Indicators')
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ActivityIndicator(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=_('Activity'), on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, verbose_name=_('Indicator'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Activity Indicator')
        verbose_name_plural = _('Activity Indicators')
        ordering = ['activity', 'indicator']
        unique_together = ['activity', 'indicator']

    def __str__(self):
        return '%s: %s' % (self.activity, self.indicator)

    def __unicode__(self):
        return '%s: %s' % (self.activity, self.indicator)
