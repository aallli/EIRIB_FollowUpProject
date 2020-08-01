from threading import Timer
from .utils import execute_query
from .models import User, Title, AccessLevel
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.backends import ModelBackend


class EIRIBBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = self.get_user_by_username(username)
        except User.DoesNotExist:
            return

        if user.check_password(password) and self.user_can_authenticate(user):
            if not user.is_secretary:
                user_query = Timer(1, self.get_user_query(user))
                user_query.start()
            return user

    def get_user_by_username(self, user_name):
        try:
            result = execute_query('SELECT * FROM tblUser WHERE tblUser.LName=?;', (user_name))
            if len(result) == 0:
                raise User.DoesNotExist

            result = result[0]
            user = None
            try:
                user = get_user_model()._default_manager.get_by_natural_key(user_name)
            except:
                pass

            title = None
            for t in enumerate(Title):
                if t[1].label == result.envan:
                    title = t[1]
                    break
            title = title or Title.MR
            if result.AccessLevelID == 4:
                access_level = AccessLevel.SECRETARY
            else:
                access_level = AccessLevel.USER

            if user:
                user.first_name = result.FName
                user.last_name = result.LName
                user.moavenat = result.Moavenat
                user.query_name = result.openningformP
                user.access_level = access_level
                user._title = title
                user.save()
            else:
                user = User.objects.create(username=user_name, first_name=result.FName, last_name=result.LName,
                                           moavenat=result.Moavenat, query=[], query_name=result.openningformP,
                                           access_level=access_level, _title=title, is_staff=True)
                user.set_password(result.Password)
                for p in Permission.objects.all():
                    if p.name in [
                        'Can view Session',
                        'Can view Assigner',
                        'Can view Subject',
                        'Can view Actor',
                        'Can view Supervisor',
                        'Can view Attachment',
                        'Can add Attachment',
                        'Can change Attachment',
                        'Can delete Attachment',
                        'Can view Enactment', 'Can change Enactment',
                        # 'Can delete Enactment', 'Can add Enactment',
                    ] and user.is_secretary:
                        user.user_permissions.add(p)

                    if p.name in [
                        'Can view Enactment',
                        'Can change Enactment',
                        'Can view Attachment',
                        'Can add Attachment',
                        'Can change Attachment',
                        'Can delete Attachment',
                    ]:
                        user.user_permissions.add(p)

                user.save()
        except User.DoesNotExist:
            raise User.DoesNotExist

        return user

    def get_user_query(self, user):
        command = 'SELECT * from %s' % user.query_name
        result = execute_query(command)
        user.query = [r.ID for r in result]
        user.save()


class ModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
