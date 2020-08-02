from threading import Timer
from django.conf import settings
from .models import Enactment, Session, Assigner, Subject, Actor, Supervisor
from EIRIB_FollowUpProject.utils import execute_query
from django.utils.translation import ugettext_lazy as _

msgid = _('welcome')
settings.WITHOUT_SESSION_TITLE = _('[Without session]')
settings.WITHOUT_ASSIGNER_TITLE = _('[Without assigner]')
settings.WITHOUT_SUBJECT_TITLE = _('[Without subject]')
settings.WITHOUT_SUPERVISOR_TITLE = _('[Without supervisor]')
msgid = _('Admin Interface')
msgid = _('Theme')
msgid = _('Themes')
msgid = _('Email address')
msgid = _('Hold down “Control”, or “Command” on a Mac, to select more than one.')
msgid = _('First, enter a username and password. Then, you’ll be able to edit more user options.')
msgid = _('The two password fields didn’t match.')
msgid = _(
    'Please enter your old password, for security’s sake, and then '
    'enter your new password twice so we can verify you typed it in '
    'correctly.')
msgid = _(
    'Raw passwords are not stored, so there is no way to see this '
    'user’s password, but you can change the password using '
    '<a href="{}">this form</a>.'
)

tries = 0
max_try = 1
max_data = 6
data_loaded = pow(2, max_data) - 1


def get_enactments():
    global data_loaded, max_data, tries, max_try

    if data_loaded != pow(2, max_data - 1) - 1:
        if tries == max_try:
            data_loaded = pow(2, max_data) - 1
            tries = -1
            return
        tries += 1
        enactments = Timer(5, get_enactments)
        enactments.start()
        return

    Enactment.objects.all().delete()
    command = 'SELECT * from tblmosavabat'
    result = execute_query(command)
    try:
        Enactment.objects.bulk_create([Enactment(**{
            'row': r.ID,
            'description': r.sharh,
            'subject': Subject.objects.get(name=settings.WITHOUT_SUBJECT_TITLE if r.muzoo in [None, ''] else r.muzoo),
            'first_actor': Actor.objects.filter(lname=r.peygiri1).first(),
            'second_actor': Actor.objects.filter(lname=r.peygiri2).first(),
            'date': r.date,
            'follow_grade': r.lozoomepeygiri,
            'result': r.natije,
            'session': Session.objects.get(
                name=settings.WITHOUT_SESSION_TITLE if r.jalaseh in [None, ''] else r.jalaseh),
            'assigner': Assigner.objects.get(
                name=settings.WITHOUT_ASSIGNER_TITLE if r.gooyandeh in [None, ''] else r.gooyandeh),
            'first_supervisor': Supervisor.objects.get(
                name=settings.WITHOUT_SUPERVISOR_TITLE if r.vahed in [None, ''] else r.vahed),
            'second_supervisor': Supervisor.objects.get(
                name=settings.WITHOUT_SUPERVISOR_TITLE if r.vahed2 in [None, ''] else r.vahed2),
            'review_date': r.review_date}) for r in result])
    except:
        tries = -1
        return
    finally:
        data_loaded ^= 32


def get_sessions():
    global data_loaded
    try:
        Session.objects.all().delete()
        query = '''
                SELECT DISTINCT tblmosavabat.jalaseh
                FROM tblmosavabat
               '''
        result = execute_query(query)
        for r in result:
            Session.objects.get_or_create(name=settings.WITHOUT_SESSION_TITLE if r.jalaseh in [None, ''] else r.jalaseh)
    finally:
        data_loaded ^= 1


def get_assigners():
    global data_loaded
    Assigner.objects.all().delete()
    try:
        query = '''
                SELECT DISTINCT tblmosavabat.gooyandeh
                FROM tblmosavabat
               '''
        result = execute_query(query)
        for r in result:
            Assigner.objects.get_or_create(
                name=settings.WITHOUT_ASSIGNER_TITLE if r.gooyandeh in [None, ''] else r.gooyandeh)
    finally:
        data_loaded ^= 2


def get_subjects():
    global data_loaded

    try:
        Subject.objects.all().delete()
        query = '''
                SELECT DISTINCT tblmosavabat.muzoo
                FROM tblmosavabat
               '''
        result = execute_query(query)
        for r in result:
            Subject.objects.get_or_create(
                name=settings.WITHOUT_SUBJECT_TITLE if r.muzoo in [None, ''] else r.muzoo)
    finally:
        data_loaded ^= 4


def get_actors():
    global data_loaded
    try:
        Actor.objects.all().delete()
        query = '''
                SELECT tblUser.FName, tblUser.LName
                FROM tblUser
               '''
        result = execute_query(query)
        for r in result:
            Actor.objects.get_or_create(fname=r.FName, lname=r.LName)
    finally:
        data_loaded ^= 8


def get_supervisors():
    global data_loaded
    try:
        Supervisor.objects.all().delete()
        query = '''
                SELECT DISTINCT tblmosavabat.vahed AS vahed
                FROM tblmosavabat;

                UNION

                SELECT DISTINCT tblmosavabat.vahed2 AS vahed
                FROM tblmosavabat;
                '''
        result = execute_query(query)
        for r in result:
            Supervisor.objects.get_or_create(
                name=settings.WITHOUT_SUPERVISOR_TITLE if r.vahed in [None, ''] else r.vahed)
    finally:
        data_loaded ^= 16


def update_data():
    global data_loaded, tries
    data_loaded = 0
    tries = 0

    sessions = Timer(1, get_sessions)
    sessions.start()

    assigners = Timer(1, get_assigners)
    assigners.start()

    subjects = Timer(1, get_subjects)
    subjects.start()

    actors = Timer(1, get_actors)
    actors.start()

    supervisors = Timer(1, get_supervisors)
    supervisors.start()

    enactments = Timer(5, get_enactments)
    enactments.start()


def data_loading():
    global data_loaded, max_data, tries
    return data_loaded != pow(2, max_data) - 1, tries == -1
