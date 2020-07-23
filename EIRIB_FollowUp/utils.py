from threading import Timer
from django.conf import settings
from .models import Enactment, Session, Assigner, Subject, Actor

from EIRIB_FollowUpProject.utils import execute_query
from django.utils.translation import ugettext_lazy as _

msgid = _('welcome')
settings.WITHOUT_SESSION_TITLE = _('[Without session]')
settings.WITHOUT_ASSIGNER_TITLE = _('[Without assigner]')
settings.WITHOUT_SUBJECT_TITLE = _('[Without subject]')
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

max_data = 5
data_loaded = max_data


def get_enactments():
    global data_loaded
    Enactment.objects.all().delete()
    command = 'SELECT * from tblmosavabat'
    result = execute_query(command)
    Enactment.objects.bulk_create([Enactment(**{
        'row': r.ID,
        'description': r.sharh,
        'subject': Subject.objects.get(name=settings.WITHOUT_SUBJECT_TITLE if r.muzoo in [None, ''] else r.muzoo),
        'first_actor': Actor.objects.filter(lname=r.peygiri1).first(),
        'second_actor': Actor.objects.filter(lname=r.peygiri2).first(),
        'date': r.tarikh,
        'follow_grade': r.lozoomepeygiri,
        'result': r.natije,
        'session': Session.objects.get(name=settings.WITHOUT_SESSION_TITLE if r.jalaseh in [None, ''] else r.jalaseh),
        'assigner': Assigner.objects.get(
            name=settings.WITHOUT_ASSIGNER_TITLE if r.gooyandeh in [None, ''] else r.gooyandeh),
        'first_supervisor': r.vahed,
        'second_supervisor': r.vahed2,
        'review_date': r.TarikhBaznegari}) for r in result])
    data_loaded += 1


def get_sessions():
    global data_loaded
    Session.objects.all().delete()
    query = '''
            SELECT DISTINCT tblmosavabat.jalaseh
            FROM tblmosavabat
           '''
    result = execute_query(query)
    for r in result:
        Session.objects.get_or_create(name=settings.WITHOUT_SESSION_TITLE if r.jalaseh in [None, ''] else r.jalaseh)
    data_loaded += 1


def get_assigners():
    global data_loaded
    Assigner.objects.all().delete()
    query = '''
            SELECT DISTINCT tblmosavabat.gooyandeh
            FROM tblmosavabat
           '''
    result = execute_query(query)
    for r in result:
        Assigner.objects.get_or_create(
            name=settings.WITHOUT_ASSIGNER_TITLE if r.gooyandeh in [None, ''] else r.gooyandeh)
    data_loaded += 1


def get_subjects():
    global data_loaded
    Subject.objects.all().delete()
    query = '''
            SELECT DISTINCT tblmosavabat.muzoo
            FROM tblmosavabat
           '''
    result = execute_query(query)
    for r in result:
        Subject.objects.get_or_create(
            name=settings.WITHOUT_SUBJECT_TITLE if r.muzoo in [None, ''] else r.muzoo)
    data_loaded += 1


def get_actors():
    global data_loaded
    Actor.objects.all().delete()
    query = '''
            SELECT tblUser.FName, tblUser.LName
            FROM tblUser
           '''
    result = execute_query(query)
    for r in result:
        Actor.objects.get_or_create(fname=r.FName, lname=r.LName)
    data_loaded += 1


def update_data():
    global data_loaded
    data_loaded = 0

    sessions = Timer(1, get_sessions)
    sessions.start()

    assigners = Timer(1, get_assigners)
    assigners.start()

    subjects = Timer(1, get_subjects)
    subjects.start()

    actors = Timer(1, get_actors)
    actors.start()

    while(True):
        if data_loaded == max_data - 1:
            enactments = Timer(1, get_enactments)
            enactments.start()
            break


def data_loading():
    global data_loaded, max_data
    return data_loaded != max_data
