from django.contrib.auth.models import User
from models import Users


class MockBackend(object):

    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(username, password):
        user = Users.all().filter(username=username, password=password)
        if (user):
            try:
                authUser = User.objects.get(username=username)
            except User.DoesNotExist:
                authUser = User(username=username, password='mockingsite')
                authUser.is_staff = True
                authUser.save()
            return authUser
        return None
