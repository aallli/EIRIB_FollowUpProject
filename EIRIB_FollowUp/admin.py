from EIRIB_FollowUp.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from jalali_date.admin import ModelAdminJalaliMixin
from django.utils.translation import ugettext_lazy as _


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True

    class Media:
        js = ('js/custom_admin.js',)


@admin.register(User)
class UserAdmin(ModelAdminJalaliMixin, UserAdmin, BaseModelAdmin):
    fieldsets = (
        (_('Personal info'), {
            'fields': (('username', 'first_name', 'last_name', '_title'),
                       ('access_level', 'is_active'),)}),
        (_('Address Info'), {
            'fields': (('moavenat', 'email', 'query_name'))}),
        (_('Important dates'), {
            'fields': (('last_login_jalali', 'date_joined_jalali'),)}),
        (_('Permissions'), {
            'fields': (('is_staff', 'is_superuser'), 'groups', 'user_permissions'), }),
        (_('Sensitive Info'), {'fields': ('password',)}),
    )
    list_filter = ('moavenat', 'access_level', 'is_active', 'is_superuser', 'groups', 'query_name')
    readonly_fields = ['last_login_jalali', 'date_joined_jalali']
