from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from tokens import token_generator


class TokenBackend(ModelBackend):

    def authenticate(self, username, token):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if not user.is_active:
            return None

        if token_generator.check_token(user, token):
            return user
        return None
