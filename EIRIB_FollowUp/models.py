import locale
from django.db import models
from EIRIB_FollowUpProject.utils import to_jalali
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

locale.setlocale(locale.LC_ALL, '')


class AccessLevel(models.TextChoices):
    USER = 'user', _('User')
    SECRETARY = 'secretary', _('Secretary')


class Title(models.TextChoices):
    MR = 'Mr', _('Mr')
    MRS = 'Mrs', _('Mrs')


class User(AbstractUser):
    moavenat = models.CharField(verbose_name=_('Moavenat'), max_length=200, blank=True, null=True)
    access_level = models.CharField(verbose_name=_('Access Level'), choices=AccessLevel.choices,
                                    default=AccessLevel.USER, max_length=20, null=False)
    _title = models.CharField(verbose_name=_('Title'), choices=Title.choices,
                              default=Title.MR, max_length=10, null=False)
    query_name = models.CharField(verbose_name=_('Query Name'), max_length=200, blank=False, unique=True)

    def last_login_jalali(self):
        return to_jalali(self.last_login)

    last_login_jalali.short_description = _('last login')

    def date_joined_jalali(self):
        return to_jalali(self.date_joined)

    date_joined_jalali.short_description = _('date joined')

    def title(self):
        return Title(self._title).label


class Enactment(models.Model):
    row = models.IntegerField(verbose_name=_('Row'), default=1, blank=False, unique=True)
    code = models.IntegerField(verbose_name=_('Code'), default=1, blank=False)
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)
    subject = models.CharField(verbose_name=_('Subject'), max_length=4000, blank=True, null=True)
    first_actor = models.CharField(verbose_name=_('First Actor'), max_length=200, blank=True, null=True)
    second_actor = models.CharField(verbose_name=_('Second Actor'), max_length=200, blank=True, null=True)
    date = models.CharField(verbose_name=_('Assignment Date'), max_length=10, blank=True, null=True)
    follow_grade = models.CharField(verbose_name=_('Follow Grade'), max_length=10, blank=True, null=True)
    result = models.TextField(verbose_name=_('Result'), max_length=4000, blank=True, null=True)
    session = models.CharField(verbose_name=_('Session'), max_length=200, blank=True, null=True)
    assigner = models.CharField(verbose_name=_('Task Assigner'), max_length=200, blank=True, null=True)
    first_supervisor = models.CharField(verbose_name=_('First Supervisor'), max_length=200, blank=True, null=True)
    second_supervisor = models.CharField(verbose_name=_('Second Supervisor'), max_length=200, blank=True, null=True)
    review_date = models.CharField(verbose_name=_('Review Date'), max_length=10, null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Enactment')
        verbose_name_plural = _('Enactments')
        ordering = ['date', 'description']

    def __str__(self):
        return '%s: %s' % (self.session, self.row)

    def __unicode__(self):
        return '%s: %s' % (self.session, self.row)
