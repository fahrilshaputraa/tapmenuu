import uuid

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from accounts.models import Role, UserProfile


class TapMenuSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for Google OAuth.

    - Sets is_staff=True on new social account users
    - Creates a UserProfile with role=OWNER for first-time Google login
    - Skips UserProfile creation if one already exists (returning user)
    """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Ensure Google-authenticated users have staff access to the dashboard
        if not user.is_staff:
            user.is_staff = True
            user.save(update_fields=['is_staff'])
        # Create UserProfile if this is a first-time Google login
        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user, role=Role.OWNER)
        return user

    def get_login_redirect_url(self, request):
        return '/dashboard/'

    def populate_username(self, request, user):
        """Auto-generate a unique username from the Google email."""
        email = user.email or ''
        base = email.split('@')[0].replace('.', '_').replace('-', '_') or 'user'
        username = f"{base}_{uuid.uuid4().hex[:6]}"
        while self.username_exists(request, username):
            username = f"{base}_{uuid.uuid4().hex[:6]}"
        user.username = username
