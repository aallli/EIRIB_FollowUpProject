import datetime
from django.contrib import admin
from django.utils import timezone
from jalali_date import datetime2jalali
from django.db.transaction import atomic
from django.contrib.admin import SimpleListFilter
from jalali_date.admin import ModelAdminJalaliMixin
from EIRIB_FollowUpProject.utils import execute_query
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from EIRIB_FollowUp.models import User, Enactment, AccessLevel, Session, Assigner, Subject, Actor, Supervisor, \
    Attachment


class JalaliDateFilter(SimpleListFilter):
    title = _('Review Date')
    parameter_name = 'review_date'

    def lookups(self, request, model_admin):
        return [('today', _('Today')), ('this_week', _('This week')), ('10days', _('Last 10 days')),
                ('this_month', _('This month')), ('30days', _('Last 30 days'))]

    def queryset(self, request, queryset):
        startdate = timezone.now()
        enddate = None
        if self.value() == 'today':
            enddate = startdate

        if self.value() == 'this_week':
            enddate = startdate - datetime.timedelta(days=(startdate.weekday() + 2) % 7)

        if self.value() == '10days':
            enddate = startdate - datetime.timedelta(days=9)

        if self.value() == 'this_month':
            enddate = startdate - datetime.timedelta(days=datetime2jalali(startdate).day - 1)

        if self.value() == '30days':
            enddate = startdate - datetime.timedelta(days=29)

        return queryset.filter(review_date__range=[enddate, startdate]) if enddate else queryset


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True


@admin.register(Session)
class SessionAdmin(BaseModelAdmin):
    model = Session
    search_fields = ['name', ]


@admin.register(Assigner)
class AssignerAdmin(BaseModelAdmin):
    model = Assigner
    search_fields = ['name', ]


@admin.register(Subject)
class SubjectAdmin(BaseModelAdmin):
    model = Subject
    search_fields = ['name', ]


@admin.register(Actor)
class ActortAdmin(BaseModelAdmin):
    model = Actor
    list_display = ['fname', 'lname']
    list_display_links = ['fname', 'lname']
    search_fields = ['fname', 'lname', ]


@admin.register(Supervisor)
class SupervisorAdmin(BaseModelAdmin):
    model = Supervisor
    search_fields = ['name', ]


class AttachmentInline(admin.TabularInline):
    model = Attachment


@admin.register(Attachment)
class AttachmentAdmin(BaseModelAdmin):
    model = Attachment
    fields = ['description', 'file', 'enactment']
    search_fields = ['description', 'file',
                     'enactment__session__name', 'enactment__code', 'enactment__subject__name',
                     'enactment__assigner__name', 'enactment__description', 'enactment__result',
                     'enactment__first_actor__fname', 'enactment__first_actor__lname', 'enactment__second_actor__fname',
                     'enactment__second_actor__lname', 'enactment__first_supervisor__name',
                     'enactment__second_supervisor__name', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enactment" and not (request.user.is_superuser or request.user.is_secretary):
            kwargs["queryset"] = Enactment.objects.filter(row__in=request.user.query)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(User)
class UserAdmin(ModelAdminJalaliMixin, _UserAdmin, BaseModelAdmin):
    fieldsets = (
        (_('Personal info'), {
            'fields': (('username', 'first_name', 'last_name', '_title'),
                       ('access_level', 'is_active'),)}),
        (_('Address Info'), {
            'fields': (('moavenat', 'email', ('query_name', 'query')))}),
        (_('Important dates'), {
            'fields': (('last_login_jalali', 'date_joined_jalali'),)}),
        (_('Permissions'), {
            'fields': (('is_staff', 'is_superuser'), 'groups', 'user_permissions'), }),
        (_('Sensitive Info'), {'fields': ('password',)}),
    )
    list_display = ['username', 'first_name', 'last_name', 'access_level', 'moavenat', 'last_login_jalali']
    list_display_links = ['username', 'first_name', 'last_name', 'access_level', 'moavenat', 'last_login_jalali']
    list_filter = ('moavenat', 'access_level', 'is_active', 'is_superuser', 'groups', 'query_name')
    readonly_fields = ['query', 'last_login_jalali', 'date_joined_jalali']

    @atomic
    def save_model(self, request, obj, form, change):
        if obj.pk:
            query = '''
                    UPDATE tblUser
                    SET tblUser.FName = ?
                    , tblUser.LName = ?
                    , tblUser.Moavenat = ?
                    , tblUser.openningformP = ?
                    , tblUser.AccessLevelID = ?
                    , tblUser.envan = ?
                    WHERE UserID = ?
                   '''
            params = (obj.first_name, obj.last_name, obj.moavenat, obj.query_name,
                      1 if obj.access_level == AccessLevel.USER else 4, str(obj.title()), obj.user_id)
        else:
            query = '''
                    INSERT INTO tblUser (LName, Password, openningformP, P)
                    VALUES(?, ?, ?, ?)
                    '''
            obj.last_name = obj.username
            obj.query_name = obj.username
            params = (obj.last_name, obj._password, obj.query_name, 'p')

        obj.user_id = execute_query(query, params, insert=True)
        super(UserAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        query = '''
                DELETE FROM tblUser
                WHERE tblUser.UserID = ?
                '''
        params = (obj.user_id)
        execute_query(query, params, True)
        super(UserAdmin, self).delete_model(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(UserAdmin, self).get_form(request, obj=obj, **kwargs)
        if request.user.is_secretary and not request.user.is_superuser:
            self.readonly_fields += ['is_staff', 'is_superuser', 'groups', 'user_permissions']
        return form


@admin.register(Enactment)
class EnactmentAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Enactment
    fields = (('row', 'session', 'date', 'review_date'),
              ('assigner', 'subject'),
              'description', 'result',
              ('first_actor', 'second_actor', 'follow_grade'),
              ('first_supervisor', 'second_supervisor', 'code'),
              )
    list_display = ['row', 'session', 'review_date_jalali', 'subject', 'description_short',
                    'result_short']
    list_display_links = ['row', 'session', 'review_date_jalali', 'subject', 'description_short',
                          'result_short']
    list_filter = [JalaliDateFilter, 'follow_grade', 'session', 'subject', 'assigner', 'first_actor',
                   'first_supervisor']
    search_fields = ['session__name', 'subject__name', 'assigner__name', 'description', 'result',
                     'first_actor__fname', 'first_actor__lname', 'second_actor__fname', 'second_actor__lname',
                     'first_supervisor__name', 'second_supervisor__name', ]
    inlines = [AttachmentInline, ]
    readonly_fields = ['description_short', 'result_short', 'review_date_jalali', ]

    def get_queryset(self, request):
        if request.user.is_superuser or request.user.is_secretary:
            return Enactment.objects.all()

        return Enactment.objects.filter(row__in=request.user.query)

    def get_form(self, request, obj=None, **kwargs):
        form = super(EnactmentAdmin, self).get_form(request, obj=obj, **kwargs)
        if not (request.user.is_superuser or request.user.is_secretary):
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
                SET tblmosavabat.natije = ?
               '''

        if request.user.is_superuser or request.user.is_secretary:
            query += ", tblmosavabat.sharh='%s' " % obj.description

            if obj.first_actor:
                query += ", tblmosavabat.peygiri1='%s' " % obj.first_actor.lname
            else:
                query += ", tblmosavabat.peygiri1='' "

            if obj.second_actor:
                query += ", tblmosavabat.peygiri2='%s' " % obj.second_actor.lname
            else:
                query += ", tblmosavabat.peygiri2='' "

            query += ", tblmosavabat.[date]='%s' " % obj.date
            query += ", tblmosavabat.lozoomepeygiri='%s' " % obj.follow_grade
            query += ", tblmosavabat.jalaseh='%s' " % obj.session.name
            query += ", tblmosavabat.muzoo='%s' " % obj.subject.name
            query += ", tblmosavabat.gooyandeh='%s' " % obj.assigner.name

            if obj.first_supervisor:
                query += ", tblmosavabat.vahed='%s' " % obj.first_supervisor.name
            else:
                query += ", tblmosavabat.vahed='' "

            if obj.second_supervisor:
                query += ", tblmosavabat.vahed2='%s' " % obj.second_supervisor.name
            else:
                query += ", tblmosavabat.vahed2='' "

            query += ", tblmosavabat.mosavabatcode=%s " % obj.code
            query += ", tblmosavabat.review_date='%s' " % obj.review_date

        params = (obj.result, obj.row)
        query += '''
                WHERE ID = ?
               '''
        execute_query(query, params, True)
        super(EnactmentAdmin, self).save_model(request, obj, form, change)

    @atomic
    def save_formset(self, request, form, formset, change):
        super(EnactmentAdmin, self).save_formset(request, form, formset, change)
        if formset.prefix == 'attachment_set' and change:
            obj = form.instance
            query = '''
                UPDATE tblmosavabat
                SET tblmosavabat.[attachments] = ?
               '''

            attachments = ' '.join(
                '%s%s' % (request.META['HTTP_ORIGIN'], attachment.file.url) for attachment in obj.attachment_set.all())

            params = (attachments, obj.row)
            query += '''
                    WHERE ID = ?
                   '''
            execute_query(query, params, True)
