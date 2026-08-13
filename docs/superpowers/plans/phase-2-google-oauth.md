# Plan: Phase 2 — Google OAuth Integration

## Goal

Add Google OAuth login for owner/admin staff using `django-allauth`. Staff can sign in with their Google account. First-time Google login creates a UserProfile with role=OWNER and redirects to dashboard. Existing email/password flow is unchanged.

## Dependencies

- `django-allauth==65.3.0` — OAuth2 + social account management
- Credentials stored in `.env` (already done)

## Decisions

1. Google OAuth is for owner/admin only — no customer-facing use
2. First Google login → creates UserProfile + role=OWNER, redirects to dashboard
3. If Google email already exists as a staff account → logs in normally
4. No social account linking UI needed — just login
5. Allauth handles the OAuth callback, we hook into `ACCOUNT_ADAPTER` to create UserProfile

## What Changes

### 1. Install dependency

```bash
.venv/bin/pip install django-allauth==65.3.0
```

Add to requirements or pyproject.toml.

### 2. Settings (`core/settings.py`)

Add to `INSTALLED_APPS`:
```python
'django.contrib.sites',
'allauth',
'allauth.account',
'allauth.socialaccount',
'allauth.socialaccount.providers.google',
```

Add settings:
```python
SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_LOGIN_ON_GET = True
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_EMAIL_VERIFICATION = 'none'
```

### 3. Load .env in settings

```python
from dotenv import load_dotenv
load_dotenv()
```

Install `python-dotenv==1.0.1`.

### 4. URLs (`core/urls.py`)

Add allauth URLs:
```python
path('accounts/', include('allauth.urls')),
```

### 5. Custom Social Account Adapter (`accounts/adapters.py`)

Hook into allauth's post-login to create UserProfile:

```python
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from accounts.models import Role, UserProfile
from restaurants.models import Restaurant

class TapMenuSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.is_staff = True
        user.save(update_fields=['is_staff'])
        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user, role=Role.OWNER)
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        return '/dashboard/'
```

Add to settings:
```python
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.TapMenuSocialAccountAdapter'
```

### 6. Migration

```bash
.venv/bin/python manage.py migrate
```

This creates `sites`, `socialaccount`, and related tables.

### 7. Create Site object

```bash
.venv/bin/python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(id=1, defaults={'domain': 'localhost:8111', 'name': 'TapMenu Dev'})
"
```

### 8. Login template — add Google button

Update `core/templates/core/pages/login.html` to wire the Google button to allauth:

```html
<a href="{% url 'google_login' %}" ...>
    Masuk dengan Google
</a>
```

Actually use the allauth URL: `{% url 'socialaccount_signup' %}` or `{% provider_login_url 'google' %}`.

### 9. Register template — add Google button

Same — wire "Daftar dengan Google" button to allauth Google login URL.

### 10. Tests (`accounts/tests.py`)

Add tests:
- Google OAuth redirect URL returns 302
- Social account adapter sets is_staff=True
- Social account adapter creates UserProfile with role=OWNER

## File Checklist

| File | Change |
|------|--------|
| `requirements-dev.txt` or `pyproject.toml` | Add django-allauth, python-dotenv |
| `core/settings.py` | INSTALLED_APPS, allauth settings, dotenv load |
| `core/urls.py` | Add allauth.urls |
| `accounts/adapters.py` | NEW — TapMenuSocialAccountAdapter |
| `core/templates/core/pages/login.html` | Wire Google button to allauth URL |
| `core/templates/core/pages/register.html` | Wire Google button to allauth URL |
| `accounts/tests.py` | Add Google OAuth tests |

## Verification

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py migrate
.venv/bin/python manage.py test accounts
```

## Out of Scope (Phase 3)

- Onboarding wizard (restaurant name → tema → karyawan)
- Password reset via email
