import pyodbc
from jalali_date import datetime2jalali
from EIRIB_FollowUpProject import settings
from django.utils.translation import ugettext_lazy as _


def get_admin_url(self):
    """the url to the Django admin interface for the model instance"""
    from django.urls import reverse

    info = (self._meta.app_label, self._meta.model_name)
    return reverse('admin:%s_%s_change' % info, args=(self.pk,))


def to_jalali(date, no_time=False):
    if date:
        if no_time:
            return datetime2jalali(date).strftime('%Y/%m/%d')
        else:
            return datetime2jalali(date).strftime('%H:%M:%S %Y/%m/%d')
    return ''


def mdb_connect(db_file, user='admin', password='', old_driver=False):
    driver_ver = '*.mdb'
    if not old_driver:
        driver_ver += ', *.accdb'

    odbc_conn_str = ('DRIVER={Microsoft Access Driver (%s)}'
                     ';DBQ=%s;UID=%s;PWD=%s' %
                     (driver_ver, db_file, user, password))

    return pyodbc.connect(odbc_conn_str)


conn = mdb_connect(settings.DATABASES['access']['NAME'])


def execute_query(query, params=None, update=None, insert=None, delete=None):
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)

    if update:
        conn.commit()
        result = _("Update failed.") if cur.rowcount == -1 else _("Successful update.")
    elif insert:
        conn.commit()
        cur.execute('SELECT @@IDENTITY;')
        result = cur.fetchone()[0]
    elif delete:
        conn.commit()
        result = _("Delete failed.") if cur.rowcount == -1 else _("Successful delete.")
    else:
        result = cur.fetchall()

    cur.close()
    return result


def switch_lang_code(path, language):
    # Get the supported language codes
    lang_codes = [c for (c, name) in settings.LANGUAGES]

    # Validate the inputs
    if path == '':
        raise Exception('URL path for language switch is empty')
    elif path[0] != '/':
        raise Exception('URL path for language switch does not start with "/"')
    elif language not in lang_codes:
        raise Exception('%s is not a supported language code' % language)

    # Split the parts of the path
    parts = path.split('/')

    # Add or substitute the new language prefix
    if parts[1] in lang_codes:
        parts[1] = language
    else:
        parts[0] = "/" + language

    # Return the full new path
    return '/'.join(parts)
