from .models import User, Enactment, Title, AccessLevel
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.backends import ModelBackend
from EIRIB_FollowUpProject.utils import execute_query


class EIRIBBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = self.get_user_by_username(username)
        except User.DoesNotExist:
            return

        if user.check_password(password) and self.user_can_authenticate(user):
            self.get_enactments(user)
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

            title = None
            for t in enumerate(Title):
                if t[1].label == result.envan:
                    title = t[1]
                    break
            access_level = None
            if result.AccessLevelID==4:
                access_level= AccessLevel.SECRETARY
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
                                           moavenat=result.Moavenat, query_name=result.openningformP,
                                           access_level=access_level, _title=title, is_staff=True)
                user.set_password(result.Password)
                for p in Permission.objects.all():
                    if p.name in ['Can view Enactment', 'Can change Enactment', 'Can delete Enactment',
                                  'Can add Enactment']:
                        user.user_permissions.add(p)
                user.save()
        except User.DoesNotExist:
            raise User.DoesNotExist
        except Exception:
            return None

        return user

    def get_enactments(self, user):
        Enactment.objects.filter(user=user).delete()
        command = 'SELECT * from %s' % user.query_name
        result = execute_query(command)
        for r in result:
            Enactment.objects.create(row=r.ID,
                                     description=r.sharh,
                                     subject=r.muzoo,
                                     first_actor=r.peygiri1,
                                     second_actor=r.peygiri2,
                                     date=r.tarikh,
                                     follow_grade=r.lozoomepeygiri,
                                     result=r.natije,
                                     session=r.jalaseh,
                                     assigner=r.gooyandeh,
                                     first_supervisor=r.vahed,
                                     second_supervisor=r.vahed2,
                                     review_date=r.TarikhBaznegari,
                                     user=user)
