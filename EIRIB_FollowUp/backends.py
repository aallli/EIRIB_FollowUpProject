from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from EIRIB_FollowUpProject.utils import execute_query
from .models import User


class EIRIBBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = self.get_user_by_username(username)
        except User.DoesNotExist:
            return

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

    def get_user_by_username(self, user_name):
        try:
            result = execute_query('SELECT * FROM tblUser WHERE (((tblUser.LName)=?));', (user_name))
            if len(result) == 0:
                raise User.DoesNotExist

            result = result[0]
            user = None
            try:
                user = get_user_model()._default_manager.get_by_natural_key(user_name)
            except:
                pass

            if user:
                user.first_name = result.FName
                user.last_name = result.LName
                user.moavenat = result.Moavenat
                user.query_name = result.openningformP
                user.save()
            else:
                user = User.objects.create(username=user_name, first_name=result.FName, last_name=result.LName,
                                           moavenat=result.Moavenat, query_name=result.openningformP, is_staff=True)
                user.set_password(result.Password)
                user.save()
        except User.DoesNotExist:
            raise User.DoesNotExist
        except Exception:
            return None

        return user
