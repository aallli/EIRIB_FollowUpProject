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
