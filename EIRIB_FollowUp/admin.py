from django.contrib import admin
from django.db.transaction import atomic
from jalali_date.admin import ModelAdminJalaliMixin
from EIRIB_FollowUpProject.utils import execute_query
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from EIRIB_FollowUp.models import User, Enactment, AccessLevel, Session, Assigner


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True

    class Media:
        js = ('js/custom_admin.js',)


@admin.register(Session)
class SessionAdmin(BaseModelAdmin):
    model = Session


@admin.register(Assigner)
class AssignerAdmin(BaseModelAdmin):
    model = Assigner


@admin.register(User)
class UserAdmin(ModelAdminJalaliMixin, _UserAdmin, BaseModelAdmin):
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


@admin.register(Enactment)
class EnactmentAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Enactment
    fields = (('row', 'session', 'date', 'review_date'),
              ('assigner', 'subject'),
              'description', 'result',
              ('first_actor', 'second_actor', 'follow_grade'),
              ('first_supervisor', 'second_supervisor', 'code'),
              )
    list_display = ['row', 'session', 'date', 'code', 'subject']
    list_display_links = ['row', 'session', 'date', 'code', 'subject']
    list_filter = ['follow_grade', ]
    search_fields = ['session', 'code', 'subject', 'assigner', 'description', 'result', 'first_actor', 'second_actor',
                     'first_supervisor', 'second_supervisor']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Enactment.objects.all()

        command = 'SELECT * from %s' % request.user.query_name
        result = execute_query(command)
        valid_rows = [r.ID for r in result]
        return Enactment.objects.filter(row__in=valid_rows)

    def get_form(self, request, obj=None, **kwargs):
        form = super(EnactmentAdmin, self).get_form(request, obj=obj, **kwargs)
        if not request.user.is_superuser and request.user.access_level == AccessLevel.USER:
            self.readonly_fields = ['row', 'code', 'session', 'date', 'review_date', 'assigner', 'subject',
                                    'description',
                                    'first_actor', 'second_actor', 'follow_grade', 'first_supervisor',
                                    'second_supervisor']
        else:
            self.readonly_fields = ['row']

        return form

    @atomic
    def save_model(self, request, obj, form, change):
        query = '''
                UPDATE tblmosavabat
                SET natije = ?
               '''
        if request.user.is_superuser or request.user.access_level == AccessLevel.SECRETARY:
            query += ", sharh='%s' " % obj.description
            query += ", peygiri1='%s' " % obj.first_actor
            query += ", peygiri2='%s' " % obj.second_actor
            query += ", tarikh=%s " % obj.date
            query += ", lozoomepeygiri='%s' " % obj.follow_grade
            query += ", jalaseh='%s' " % obj.session
            query += ", muzoo='%s' " % obj.subject
            query += ", gooyandeh='%s' " % obj.assigner
            query += ", vahed='%s' " % obj.first_supervisor
            query += ", vahed2='%s' " % obj.second_supervisor
            query += ", mosavabatcode=%s " % obj.code
            query += ", TarikhBaznegari = '%s' " % obj.review_date
        params = (obj.result, obj.row)
        query += '''
                WHERE ID = ?
               '''
        execute_query(query, params, True)
        super(EnactmentAdmin, self).save_model(request, obj, form, change)
