# Plan: Phase 3 — Onboarding Wizard

## Goal

Show a 3-step onboarding wizard to any owner who logs in (via email/password or Google) and has `UserProfile.restaurant == None`. After completing or skipping all steps, redirect to dashboard with a success toast. Dashboard shows a warning banner if the restaurant profile is incomplete. Sidebar shows the real restaurant name from the owner's UserProfile.

## Trigger

Any view decorated with `@staff_required` or `@role_required` checks:
- If `request.user.profile.restaurant is None` → redirect to `/onboarding/`
- If restaurant exists → proceed normally

## Steps

| Step | URL | Required | Skippable |
|------|-----|----------|-----------|
| 1 — Profil Toko | `/onboarding/` | Nama restaurant | Deskripsi, telepon, logo |
| 2 — Pallet Warna | `/onboarding/theme/` | - | Entire step (skip button) |
| 3 — Tambah Karyawan | `/onboarding/team/` | - | Entire step (skip button) |

## Color Palettes (10 presets)

| # | Name | primary | secondary | accent | bg | card |
|---|------|---------|-----------|--------|----|------|
| 1 | TapMenu (default) | #1B4332 | #D8F3DC | #E07A5F | #F7F5F2 | #FFFFFF |
| 2 | Sunset | #C75146 | #FFE8D6 | #F4A261 | #FFF8F0 | #FFFFFF |
| 3 | Ocean | #1A5276 | #D6EAF8 | #2E86C1 | #F0F7FF | #FFFFFF |
| 4 | Coklat Klasik | #6E3A1E | #F5E6D3 | #D4845A | #FAF5F0 | #FFFFFF |
| 5 | Merah Berani | #922B21 | #FDEDEC | #E74C3C | #FFF5F5 | #FFFFFF |
| 6 | Ungu Modern | #6C3483 | #F4ECF7 | #8E44AD | #FAF5FF | #FFFFFF |
| 7 | Hijau Segar | #1E8449 | #D5F5E3 | #27AE60 | #F0FFF4 | #FFFFFF |
| 8 | Biru Elegan | #154360 | #D6EAF8 | #1A75BB | #F0F8FF | #FFFFFF |
| 9 | Pink Manis | #943A5D | #FDEBF2 | #E91E8C | #FFF5FA | #FFFFFF |
| 10 | Abu Minimalis | #2C3E50 | #ECF0F1 | #7F8C8D | #F8F9FA | #FFFFFF |

## What Changes

### 1. New app: `onboarding/` (or views in `core/`)

Since onboarding is a one-time flow tightly coupled to `accounts` and `restaurants`, we'll add views directly to `core/views.py` and URLs to `core/urls.py` — no new app needed.

### 2. Middleware / decorator redirect (`dashboard/views.py`)

Update `_get_or_create_profile` helper and add a helper `_check_onboarding_required(request)`:

```python
def _check_onboarding_required(request):
    """Return redirect to onboarding if user has no restaurant set."""
    if not request.user.is_authenticated:
        return None
    profile = _get_or_create_profile(request.user)
    if profile.restaurant_id is None and not request.user.is_superuser:
        return redirect('onboarding_step1')
    return None
```

Call this at the top of `dashboard_home` and other relevant views. OR use a middleware approach — simpler: add check to `staff_required` wrapper.

### 3. Onboarding views (`core/views.py`)

**Step 1 — Profil Toko:**
```
GET/POST /onboarding/
```
- Fields: `restaurant_name` (required), `description`, `phone`, `logo` (all optional)
- On valid POST: create `Restaurant`, link to `UserProfile.restaurant`, redirect to step 2
- "Lanjut" button

**Step 2 — Pallet Warna:**
```
GET/POST /onboarding/theme/
```
- Shows 10 color palette cards (radio selection)
- On POST: create/update `MenuAppearanceTheme` with selected palette colors
- "Lanjut" and "Lewati" buttons

**Step 3 — Tambah Karyawan:**
```
GET/POST /onboarding/team/
```
- Shows mini employee create form (email + role)
- Can add multiple or skip entirely
- "Selesai & Masuk Dashboard" and "Lewati" buttons
- On finish: set `request.session['onboarding_complete'] = True`, redirect to dashboard

### 4. Dashboard — success toast

In `dashboard_home` view, check `request.session.pop('onboarding_complete', False)`:
- If True → pass `show_welcome_toast=True` to context
- Template renders a toast notification in top-right: "Selamat datang! Toko kamu berhasil dibuat. 🎉"

### 5. Dashboard — incomplete profile warning

In `dashboard_home` view, check if restaurant profile is "complete":
- Complete = `restaurant.name` AND `restaurant.description` AND `restaurant.phone` AND `restaurant.logo`
- If any missing → pass `profile_incomplete=True` and list of missing fields to context
- Template renders a yellow warning banner: "Profil toko belum lengkap — [isi sekarang →](/dashboard/store/)"

### 6. Sidebar — real restaurant name

The sidebar already uses `{{ restaurant.name|default:'Dashboard' }}` from `_dashboard_context()`. The issue is `_dashboard_context()` gets restaurant via `Restaurant.objects.order_by('id').first()` — not scoped to the logged-in user's restaurant.

Fix `_dashboard_context()` to use the user's restaurant:

```python
def _dashboard_context(request=None, **extra):
    restaurant = None
    if request and request.user.is_authenticated:
        profile = _get_or_create_profile(request.user)
        restaurant = profile.restaurant
    if restaurant is None:
        restaurant = Restaurant.objects.order_by('id').first()
    return {'restaurant': restaurant, **extra}
```

Update all `_dashboard_context(...)` calls to pass `request=request`.

### 7. Onboarding templates

- `core/templates/core/pages/onboarding-step1.html` — standalone page (not dashboard layout)
- `core/templates/core/pages/onboarding-step2.html`
- `core/templates/core/pages/onboarding-step3.html`

Use TapMenu design language: `bg-bg`, `text-primary`, `bg-primary`, Plus Jakarta Sans, same border-radius patterns.

### 8. URLs (`core/urls.py`)

```python
path('onboarding/', views.onboarding_step1, name='onboarding_step1'),
path('onboarding/theme/', views.onboarding_step2, name='onboarding_step2'),
path('onboarding/team/', views.onboarding_step3, name='onboarding_step3'),
```

### 9. Guard — prevent accessing onboarding after restaurant is set

If user with a restaurant visits `/onboarding/` → redirect to `/dashboard/`.

### 10. Tests (`accounts/tests.py`)

- Owner with no restaurant is redirected to onboarding when visiting dashboard
- Step 1 creates restaurant and links to UserProfile
- Step 2 creates MenuAppearanceTheme with selected palette
- Step 3 creates employee (optional)
- Skipping step 2 still proceeds to step 3
- Skipping step 3 redirects to dashboard with onboarding_complete session
- Dashboard shows welcome toast when onboarding_complete session key present
- Dashboard shows incomplete warning when restaurant fields are missing
- Sidebar shows correct restaurant name for logged-in user

## File Checklist

| File | Change |
|------|--------|
| `core/views.py` | ADD onboarding_step1/2/3 views, fix _dashboard_context restaurant scoping |
| `core/urls.py` | ADD onboarding URLs |
| `dashboard/views.py` | ADD _check_onboarding_required, update dashboard_home for toast + warning |
| `core/templates/core/pages/onboarding-step1.html` | NEW |
| `core/templates/core/pages/onboarding-step2.html` | NEW |
| `core/templates/core/pages/onboarding-step3.html` | NEW |
| `core/templates/core/pages/dashboard.html` | ADD toast + incomplete warning |
| `core/templates/core/partials/dashboard_sidebar.html` | Fix restaurant name scoping (already uses context var, just fix the source) |
| `accounts/tests.py` | ADD onboarding tests |

## Verification

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test accounts
```

All 25 existing tests must still pass + new onboarding tests.
