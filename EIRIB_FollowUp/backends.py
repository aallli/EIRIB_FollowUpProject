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
        else:
            user.delete()

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
            else:
                user = User.objects.create(user_id=result.UserID, username=user_name, first_name=result.FName,
                                           last_name=result.LName, moavenat=result.Moavenat,
                                           query_name=result.openningformP, access_level=access_level, _title=title,
                                           is_staff=True)

            self.set_permissions(user)
            user.set_password(result.Password)
            user.save()
        except User.DoesNotExist:
            raise User.DoesNotExist

        return user

    def get_user_query(self, user):
        command = 'SELECT * from %s' % user.query_name
        result = execute_query(command)
        user.query = [r.ID for r in result]
        user.save()

    def set_permissions(self, user):
        for p in Permission.objects.all():
            if p.codename in [
                'add_enactment',
                'change_enactment',
                'delete_enactment',
                'view_enactment',

                'view_attachment',
                'add_attachment',
                'change_attachment',
                'delete_attachment',
            ]:
                user.user_permissions.add(p)
            elif p.codename in [
                'view_session',
                'view_assigner',
                'view_subject',
                'view_actor',
                'view_supervisor',
                'add_user',
                'change_user',
                'delete_user',
                'view_user',
            ]:
                if user.is_secretary:
                    user.user_permissions.add(p)
                else:
                    user.user_permissions.remove(p)


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
