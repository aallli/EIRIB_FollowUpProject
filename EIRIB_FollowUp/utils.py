from threading import Timer
from django.conf import settings
from .models import Enactment, Session
from EIRIB_FollowUpProject.utils import execute_query
from django.utils.translation import ugettext_lazy as _

msgid = _('welcome')
msgid = _('[Without session]')
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

max_data = 2
data_loaded = max_data


def get_enactments():
    global data_loaded
    Enactment.objects.all().delete()
    command = 'SELECT * from tblmosavabat'
    result = execute_query(command)
    Enactment.objects.bulk_create([Enactment(**{
        'row': r.ID,
        'description': r.sharh,
        'subject': r.muzoo,
        'first_actor': r.peygiri1,
        'second_actor': r.peygiri2,
        'date': r.tarikh,
        'follow_grade': r.lozoomepeygiri,
        'result': r.natije,
        'session': Session.objects.get(name=settings.WITHOUT_SESSION_TITLE if r.jalaseh in [None, ''] else r.jalaseh),
        'assigner': r.gooyandeh,
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


def update_data():
    global data_loaded
    data_loaded = 0

    sessions = Timer(1, get_sessions)
    sessions.start()

    enactments = Timer(1, get_enactments)
    enactments.start()


def data_loading():
    global data_loaded, max_data
    return data_loaded != max_data
