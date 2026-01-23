from django.contrib.auth.backends import ModelBackend, BaseBackend

from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()
# Using the same backend models for my 

class EmailBackend(BaseBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        email = username or kwargs.get('email')
        if email is None:
            return None # This is my version of ensuring that email is required for login
        else:
            try:
                user = User.objects.get(Q(username__iexact=email) | Q(email__iexact=email))
                # This will ensure that our password is secure "password123" would
                # turn into a convoluted mess

                if user.check_password(password): 
                    return user
                else:
                    return None

            except User.DoesNotExist:
                return  None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
            