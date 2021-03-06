from django.contrib.auth.signals import user_logged_in
from cassandra.cqlengine.query import DoesNotExist
from django.contrib.auth.models import update_last_login
from django.contrib.auth.models import User
from models import Users
import logging

logger = logging.getLogger(__name__)


class MockBackend(object):

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, username, password, fbid, isInternal=False):
        try:
            user = Users.objects.get(username=username)
        except DoesNotExist:
            logger.debug("Could u believe it")
            return None
        if (user):
            logger.debug("Authenticating user: " + username)
            if (user.password == password):
                if ((user.fbid and user.fbid == fbid) or (not user.fbid)):
                    try:
                        authUser = User.objects.get(username=username)
                    except User.DoesNotExist:
                        authUser = User(username=username,
                                        password='mockingsite')
                        authUser.save()
                    if isInternal:
                        logger.debug("is staff: " + str(authUser.is_staff))
                        if authUser.is_staff:
                            return authUser
                        else:
                            return None
                    return authUser
        return None

    user_logged_in.disconnect(update_last_login)
