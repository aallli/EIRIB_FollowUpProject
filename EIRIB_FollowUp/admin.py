import datetime
from django.contrib import admin
from django.utils import timezone
from .forms import EnactmentAdminForm
from jalali_date import datetime2jalali
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.contrib.admin import SimpleListFilter
from jalali_date.admin import ModelAdminJalaliMixin
from EIRIB_FollowUpProject.admin import BaseModelAdmin
from django.utils.translation import ugettext_lazy as _
from EIRIB_FollowUpProject.utils import JalaliDateFilter
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from EIRIB_FollowUpProject.utils import execute_query, to_jalali
from EIRIB_FollowUp.models import User, Enactment, AccessLevel, Session, Assigner, Subject, Actor, Supervisor, \
    Attachment


class ReviewJalaliDateFilter(SimpleListFilter):
    title = _('Review Date')
    parameter_name = '_review_date'

    def lookups(self, request, model_admin):
        return [('today', _('Today')), ('this_week', _('This week')), ('10days', _('Last 10 days')),
                ('this_month', _('This month')), ('30days', _('Last 30 days')), ('90days', _('Last 3 months')),
                ('180days', _('Last 6 months'))]

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

        if self.value() == '90days':
            enddate = startdate - datetime.timedelta(days=89)

        if self.value() == '180days':
            enddate = startdate - datetime.timedelta(days=179)

        return queryset.filter(_review_date__range=[enddate, startdate]) if enddate else queryset


class ActorFilter(SimpleListFilter):
    title = _('Supervisor')
    parameter_name = 'actor'

    def lookups(self, request, model_admin):
        return [(actor.pk, actor) for actor in Actor.objects.all()]

    def queryset(self, request, queryset):
        return queryset.filter(first_actor__pk=self.value()) | queryset.filter(
            second_actor__pk=self.value()) if self.value() else queryset


class SupervisorFilter(SimpleListFilter):
    title = _('Supervisor Unit')
    parameter_name = 'supervisor'

    def lookups(self, request, model_admin):
        return [(supervisor.pk, supervisor.name) for supervisor in Supervisor.objects.all()]

    def queryset(self, request, queryset):
        return queryset.filter(first_actor__supervisor__pk=self.value()) | queryset.filter(
            second_actor__supervisor__pk=self.value()) if self.value() else queryset


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
    list_display = ['fname', 'lname', 'supervisor']
    list_display_links = ['fname', 'lname', 'supervisor']
    search_fields = ['fname', 'lname', 'supervisor__name']


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

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_secretary and not request.user.is_superuser:
            return self.readonly_fields + ['is_staff', 'is_superuser', 'groups', 'user_permissions']
        return self.readonly_fields

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
            execute_query(query, params, update=True)
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

    @atomic
    def delete_model(self, request, obj):
        query = '''
                DELETE FROM tblUser
                WHERE tblUser.UserID = ?
                '''
        params = (obj.user_id)
        execute_query(query, params, delete=True)
        super(UserAdmin, self).delete_model(request, obj)


@admin.register(Enactment)
class EnactmentAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Enactment
    fields = (('row', 'session', '_date', '_review_date'),
              ('assigner', 'subject', 'code'),
              'description', 'result',
              ('first_actor', 'first_supervisor'),
              ('second_actor', 'second_supervisor'),
              )
    list_display = ['row', 'session', 'date', 'review_date', 'subject', 'description_short',
                    'result_short']
    list_display_links = ['row', 'session', 'date', 'review_date', 'subject', 'description_short',
                          'result_short']
    list_filter = [ReviewJalaliDateFilter, JalaliDateFilter, 'session', 'subject', 'assigner', ActorFilter,
                   SupervisorFilter]
    search_fields = ['session__name', 'subject__name', 'assigner__name', 'description', 'result',
                     'first_actor__fname', 'first_actor__lname', 'second_actor__fname', 'second_actor__lname', 'row']
    inlines = [AttachmentInline, ]
    readonly_fields = ['row', 'description_short', 'result_short', 'date', 'review_date',
                       'first_supervisor',
                       'second_supervisor']
    form = EnactmentAdminForm

    def changelist_view(self, request, extra_context=None):
        queryset_name = '%s_query_set' % self.model._meta.model_name
        filtered_queryset_name = 'filtered_%s_query_set' % self.model._meta.model_name
        request.session[filtered_queryset_name] = False
        response = super(EnactmentAdmin, self).changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            request.session[queryset_name] = list(response.context_data["cl"].queryset.values('pk'))
            if self.get_preserved_filters(request):
                request.session[filtered_queryset_name] = True
        return response

    def get_queryset(self, request):
        queryset = Enactment.objects.filter(follow_grade=1)

        if request.session['filtered_enactment_query_set']:
            queryset = queryset.filter(pk__in=[enactment['pk'] for enactment in request.session['enactment_query_set']])

        if request.user.is_superuser or request.user.is_secretary:
            return queryset

        return queryset.filter(row__in=request.user.query)

    def get_readonly_fields(self, request, obj=None):
        if not (request.user.is_superuser or request.user.is_secretary):
            return self.readonly_fields + ['code', 'session', '_date', '_review_date', 'assigner', 'subject',
                                           'description', 'first_actor', 'second_actor', 'follow_grade']
        elif obj:
            return self.readonly_fields + ['_date', '_review_date']

        return self.readonly_fields

    @atomic
    def save_model(self, request, obj, form, change):
        new_obj = False
        if obj.pk:
            obj._review_date = timezone.now()
            query = '''
                    UPDATE tblmosavabat
                    SET tblmosavabat.natije = ?
                   '''
            params = [obj.result]

            if request.user.is_superuser or request.user.is_secretary:
                query += ", tblmosavabat.sharh=?, tblmosavabat.peygiri1=?, tblmosavabat.peygiri2=?" \
                         ", tblmosavabat.tarikh=?, tblmosavabat.jalaseh=?, tblmosavabat.muzoo=?" \
                         ", tblmosavabat.gooyandeh=?, tblmosavabat.vahed=?, tblmosavabat.vahed2=?" \
                         ", tblmosavabat.mosavabatcode=?, tblmosavabat.TarikhBaznegari=?, tblmosavabat.[date]=?" \
                         ", tblmosavabat.review_date=?"
                params.extend((obj.description,
                               obj.first_actor.lname if obj.first_actor else '-',
                               obj.second_actor.lname if obj.second_actor else '-',
                               int(to_jalali(obj._date, no_time=True).replace('/', '')) - 13000000,
                               obj.session.name,
                               obj.subject.name,
                               obj.assigner.name,
                               obj.first_actor.supervisor.name if obj.first_actor and obj.first_actor.supervisor else '-',
                               obj.second_actor.supervisor.name if obj.second_actor and obj.second_actor.supervisor else '-',
                               obj.code,
                               obj.review_date(),
                               obj._date,
                               obj._review_date))
            query += '''
                    WHERE ID = ?
                   '''
            params.append(obj.row)
            execute_query(query, params, update=True)
        else:
            query = '''
                    INSERT INTO tblmosavabat (sharh, peygiri1, peygiri2, tarikh, lozoomepeygiri, natije, jalaseh,
                    muzoo, gooyandeh, vahed, vahed2, mosavabatcode, TarikhBaznegari, [date], review_date)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
            obj.follow_grade = 1
            params = (obj.description,
                      obj.first_actor.lname if obj.first_actor else '-',
                      obj.second_actor.lname if obj.second_actor else '-',
                      int(to_jalali(obj._date, True).replace('/', '')) - 13000000,
                      obj.follow_grade,
                      obj.result,
                      obj.session.name,
                      obj.subject.name,
                      obj.assigner.name,
                      obj.first_actor.supervisor.name if obj.first_actor and obj.first_actor.supervisor else '-',
                      obj.second_actor.supervisor.name if obj.second_actor and obj.second_actor.supervisor else '-',
                      obj.code,
                      obj.review_date(),
                      obj._date,
                      obj._review_date)
            obj.row = execute_query(query, params, insert=True)
            new_obj = True

        super(EnactmentAdmin, self).save_model(request, obj, form, change)
        if new_obj:
            queryset_name = '%s_query_set' % self.model._meta.model_name
            enactment_query_set = request.session[queryset_name]
            enactment_query_set.append({'pk': obj.pk})
            request.session[queryset_name] = list(enactment_query_set)

    @atomic
    def delete_model(self, request, obj):
        query = '''
                DELETE FROM tblmosavabat
                WHERE tblmosavabat.ID = ?
                '''
        params = (obj.row)
        execute_query(query, params, delete=True)
        super(EnactmentAdmin, self).delete_model(request, obj)

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
            execute_query(query, params, update=True)

    def get_urls(self):
        urls = super(EnactmentAdmin, self).get_urls()
        from django.urls import path
        return [path('close/', self.close, name="close"), ] + urls

    @atomic
    def close(self, request):
        result = self.next(request)
        pk = int(request.GET['pk'])
        enactment = get_object_or_404(Enactment, pk=pk)
        enactment.follow_grade = 0
        enactment.save()

        query = '''
                UPDATE tblmosavabat
                SET tblmosavabat.lozoomepeygiri = ?
                WHERE ID = ?
               '''
        params = [enactment.follow_grade, enactment.row]
        execute_query(query, params, update=True)
        return result
