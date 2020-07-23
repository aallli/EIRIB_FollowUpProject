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


class Session(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return _(self.name).__str__()


class Assigner(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Task Assigner')
        verbose_name_plural = _('Task Assigners')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return _(self.name).__str__()


class Subject(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return _(self.name).__str__()


class Actor(models.Model):
    fname = models.CharField(verbose_name=_('First Name'), max_length=2000, blank=True, null=True)
    lname = models.CharField(verbose_name=_('Last Name'), max_length=2000, blank=False)

    class Meta:
        verbose_name = _('Actor')
        verbose_name_plural = _('Actors')
        ordering = ['lname', 'fname']
        unique_together = ['lname', 'fname']

    def __str__(self):
        return '%s, %s' % (self.lname, self.fname if self.fname else '-')

    def __unicode__(self):
        return '%s, %s' % (self.lname, self.fname if self.fname else '-')


class Supervisor(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Supervisor')
        verbose_name_plural = _('Supervisors')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return _(self.name).__str__()


class User(AbstractUser):
    moavenat = models.CharField(verbose_name=_('Moavenat'), max_length=200, blank=True, null=True)
    access_level = models.CharField(verbose_name=_('Access Level'), choices=AccessLevel.choices,
                                    default=AccessLevel.USER, max_length=20, null=False)
    _title = models.CharField(verbose_name=_('Title'), choices=Title.choices,
                              default=Title.MR, max_length=100, null=False)
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
    subject = models.ForeignKey(Subject, verbose_name=_('Subject'), on_delete=models.SET_NULL, null=True)
    first_actor = models.ForeignKey(Actor, verbose_name=_('First Actor'), on_delete=models.SET_NULL, blank=True,
                                    null=True, related_name='first_actor')
    second_actor = models.ForeignKey(Actor, verbose_name=_('Second Actor'), on_delete=models.SET_NULL, blank=True,
                                     null=True, related_name='second_actor')
    date = models.CharField(verbose_name=_('Assignment Date'), max_length=20, blank=True, null=True)
    follow_grade = models.CharField(verbose_name=_('Follow Grade'), max_length=100, blank=True, null=True)
    result = models.TextField(verbose_name=_('Result'), max_length=4000, blank=True, null=True)
    session = models.ForeignKey(Session, verbose_name=_('Session'), on_delete=models.SET_NULL, null=True)
    assigner = models.ForeignKey(Assigner, verbose_name=_('Task Assigner'), on_delete=models.SET_NULL, null=True)
    first_supervisor = models.ForeignKey(Supervisor, verbose_name=_('First Supervisor'), on_delete=models.SET_NULL,
                                         blank=True, null=True, related_name='first_supervisor')
    second_supervisor = models.ForeignKey(Supervisor, verbose_name=_('Second Supervisor'), on_delete=models.SET_NULL,
                                          blank=True, null=True, related_name='second_supervisor')
    review_date = models.CharField(verbose_name=_('Review Date'), max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = _('Enactment')
        verbose_name_plural = _('Enactments')
        ordering = ['date', 'description']

    def __str__(self):
        return '%s: %s' % (self.session, self.row)

    def __unicode__(self):
        return '%s: %s' % (self.session, self.row)
