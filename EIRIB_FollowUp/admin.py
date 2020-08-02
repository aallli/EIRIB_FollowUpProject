from django.contrib import admin
from django.db.transaction import atomic
from jalali_date.admin import ModelAdminJalaliMixin
from EIRIB_FollowUpProject.utils import execute_query
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from EIRIB_FollowUp.models import User, Enactment, AccessLevel, Session, Assigner, Subject, Actor, Supervisor, \
    Attachment


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
    list_display = ['row', 'session', 'date_jalali', 'review_date_jalali', 'subject', 'description_short', 'result_short']
    list_display_links = ['row', 'session', 'date_jalali', 'review_date_jalali', 'subject', 'description_short', 'result_short']
    list_filter = ['review_date', 'follow_grade', 'session', 'subject', 'assigner', 'first_actor', 'first_supervisor']
    search_fields = ['session__name', 'subject__name', 'assigner__name', 'description', 'result',
                     'first_actor__fname', 'first_actor__lname', 'second_actor__fname', 'second_actor__lname',
                     'first_supervisor__name', 'second_supervisor__name', ]
    inlines = [AttachmentInline, ]
    readonly_fields = ['description_short', 'result_short', 'date_jalali', 'review_date_jalali', ]

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
