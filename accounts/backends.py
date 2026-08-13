from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """Authenticate using email address instead of username.

    Django's default backend uses username. This backend looks up the user
    by email (case-insensitive) and verifies the password. The default
    ModelBackend is kept as a fallback for superuser/admin logins.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Django passes the form field as 'username' regardless of label
        email = username
        if not email or not password:
            return None
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Run the default password hasher to mitigate timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Should not happen once email unique is enforced, but guard anyway
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
