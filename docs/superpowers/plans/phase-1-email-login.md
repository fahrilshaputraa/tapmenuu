# Plan: Phase 1 — Email-based Login Migration

## Goal

Migrate TapMenu staff authentication from username-based to email-based login. Email becomes the primary unique identifier for all staff (owner, admin, kasir, dapur). Username remains in the Django User model but is auto-generated and hidden from the user.

## Context

- Current login: `username` + `password` (via Django's default `authenticate`)
- Current register: user inputs a name which becomes the username; email is optional
- Problem: username is globally unique across all restaurants — two restaurants cannot have a staff member with the same username (e.g. `kasir`)
- Solution: make `email` the login identifier. Email is naturally unique globally. Username becomes an internal auto-generated field.

## Decisions (agreed in grilling session)

1. Email is the login identifier for ALL staff (owner, admin, kasir, dapur)
2. Username/password flow is kept — email replaces username in the login form
3. Username is auto-generated from `{restaurant_slug}_{role}_{random4}` and hidden
4. `User.email` must be unique — enforce at the model level via a custom backend
5. Django's `authenticate()` does not support email by default — we write a custom auth backend

## What Changes

### 1. Custom Authentication Backend (`accounts/backends.py`)

```python
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username  # Django passes the identifier as 'username'
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
```

### 2. Settings (`core/settings.py`)

Add to `AUTHENTICATION_BACKENDS`:
```python
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',  # fallback for superuser/admin
]
```

### 3. Register view (`core/views.py`)

- Make `email` required (not optional)
- Validate email is unique before creating user
- Auto-generate username: `{restaurant_slug}_{role}_{uuid4()[:4]}`
- Show error if email already registered

### 4. Employee create (`dashboard/forms.py` + `dashboard/views.py`)

- Replace `username` field with `email` field in `EmployeeCreateForm`
- Auto-generate username internally: `{restaurant_slug}_{role}_{uuid4()[:4]}`
- Validate email unique across all users
- Store email on `User.email`

### 5. Login template (`core/templates/core/pages/login.html`)

- Change field label from "Email" (already correct) — no change needed visually
- Input `name` already accepts email — just ensure it POSTs as `username` to match Django's auth flow, OR change to POST as `email` and update view

### 6. Register template (`core/templates/core/pages/register.html`)

- Remove the "Nama Lengkap" field (no longer needed as username source)
- Add validation error display for duplicate email

### 7. Employee template (`core/templates/core/pages/employee.html`)

- Replace username field in add modal with email field
- Show employee email in the table instead of username (or show both)

### 8. Migration

- No model migration needed — `User.email` already exists
- Add `UNIQUE` constraint on `User.email` via a data migration or signal

### 9. Tests (`accounts/tests.py`)

- Add tests for `EmailBackend`
- Update `make_owner()` / `make_employee()` helpers to use email
- Add test: duplicate email rejected on register
- Add test: duplicate email rejected on employee create
- Add test: login with email works
- Add test: login with wrong email fails
- Add test: login with correct email but wrong password fails

## File Checklist

| File | Change |
|------|--------|
| `accounts/backends.py` | NEW — EmailBackend |
| `accounts/tests.py` | UPDATE — new email auth tests |
| `core/settings.py` | UPDATE — AUTHENTICATION_BACKENDS |
| `core/views.py` | UPDATE — register requires email, validates unique |
| `dashboard/forms.py` | UPDATE — EmployeeCreateForm uses email |
| `dashboard/views.py` | UPDATE — employee_create generates username |
| `core/templates/core/pages/login.html` | MINOR — confirm field name |
| `core/templates/core/pages/register.html` | UPDATE — remove fullname, add email validation |
| `core/templates/core/pages/employee.html` | UPDATE — email field in add modal |

## Verification

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test accounts
```

All 17 existing tests must still pass + new email auth tests added.

## Out of Scope (Phase 2+)

- Google OAuth
- Onboarding wizard
- Password reset via email
