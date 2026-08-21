import uuid

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods

from accounts.models import Role, UserProfile
from menus.models import MenuCategory, MenuItem
from restaurants.models import DiningTable, MenuAppearanceTheme, Restaurant

# 10 color palette presets for onboarding
PALETTE_PRESETS = [
    {
        'id': 'tapmenu',
        'name': 'TapMenu',
        'description': 'Hijau alami & elegan',
        'primary': '#1B4332',
        'secondary': '#D8F3DC',
        'accent': '#E07A5F',
        'bg': '#F7F5F2',
        'card': '#FFFFFF',
    },
    {
        'id': 'sunset',
        'name': 'Sunset',
        'description': 'Hangat & menyambut',
        'primary': '#C75146',
        'secondary': '#FFE8D6',
        'accent': '#F4A261',
        'bg': '#FFF8F0',
        'card': '#FFFFFF',
    },
    {
        'id': 'ocean',
        'name': 'Ocean',
        'description': 'Bersih & profesional',
        'primary': '#1A5276',
        'secondary': '#D6EAF8',
        'accent': '#2E86C1',
        'bg': '#F0F7FF',
        'card': '#FFFFFF',
    },
    {
        'id': 'coklat',
        'name': 'Coklat Klasik',
        'description': 'Tradisional & hangat',
        'primary': '#6E3A1E',
        'secondary': '#F5E6D3',
        'accent': '#D4845A',
        'bg': '#FAF5F0',
        'card': '#FFFFFF',
    },
    {
        'id': 'merah',
        'name': 'Merah Berani',
        'description': 'Energik & penuh semangat',
        'primary': '#922B21',
        'secondary': '#FDEDEC',
        'accent': '#E74C3C',
        'bg': '#FFF5F5',
        'card': '#FFFFFF',
    },
    {
        'id': 'ungu',
        'name': 'Ungu Modern',
        'description': 'Kreatif & berkelas',
        'primary': '#6C3483',
        'secondary': '#F4ECF7',
        'accent': '#8E44AD',
        'bg': '#FAF5FF',
        'card': '#FFFFFF',
    },
    {
        'id': 'hijau',
        'name': 'Hijau Segar',
        'description': 'Segar & alami',
        'primary': '#1E8449',
        'secondary': '#D5F5E3',
        'accent': '#27AE60',
        'bg': '#F0FFF4',
        'card': '#FFFFFF',
    },
    {
        'id': 'biru',
        'name': 'Biru Elegan',
        'description': 'Terpercaya & mewah',
        'primary': '#154360',
        'secondary': '#D6EAF8',
        'accent': '#1A75BB',
        'bg': '#F0F8FF',
        'card': '#FFFFFF',
    },
    {
        'id': 'pink',
        'name': 'Pink Manis',
        'description': 'Cute & ramah',
        'primary': '#943A5D',
        'secondary': '#FDEBF2',
        'accent': '#E91E8C',
        'bg': '#FFF5FA',
        'card': '#FFFFFF',
    },
    {
        'id': 'abu',
        'name': 'Abu Minimalis',
        'description': 'Modern & minimalis',
        'primary': '#2C3E50',
        'secondary': '#ECF0F1',
        'accent': '#7F8C8D',
        'bg': '#F8F9FA',
        'card': '#FFFFFF',
    },
]


def page(template_name):
    def view(request):
        return render(request, f'core/pages/{template_name}')

    return view


landing = page('landing.html')


def book_menu(request):
    restaurant = Restaurant.objects.filter(is_active=True).order_by('id').first()
    dining_table = None
    categories = MenuCategory.objects.none()
    cart_summary = {'items': [], 'total_quantity': 0, 'total_amount': 0}

    if restaurant:
        dining_table = (
            DiningTable.objects.filter(restaurant=restaurant, is_active=True)
            .order_by('id')
            .first()
        )
        active_items = MenuItem.objects.filter(
            restaurant=restaurant,
            is_active=True,
            is_available=True,
        ).order_by('sort_order', 'name')
        categories = (
            MenuCategory.objects.filter(restaurant=restaurant, is_active=True)
            .prefetch_related(Prefetch('items', queryset=active_items))
            .order_by('sort_order', 'name')
        )
        if dining_table:
            return redirect(
                reverse('customer_menu', kwargs={'qr_token': dining_table.qr_token}),
            )

    return render(
        request,
        'core/pages/book-menu.html',
        {
            'restaurant': restaurant,
            'dining_table': dining_table,
            'categories': categories,
            'menu_count': sum(category.items.all().count() for category in categories),
            'cart_summary': cart_summary,
        },
    )


@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            auth_login(request, user)
            return redirect(request.GET.get('next') or reverse('dashboard'))
        messages.error(request, 'Email/username atau password tidak valid.')

    return render(request, 'core/pages/login.html')


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        password1 = request.POST.get('password1') or request.POST.get('password')
        password2 = request.POST.get('password2') or request.POST.get(
            'confirm_password'
        )
        restaurant_name = request.POST.get('restaurant_name') or request.POST.get(
            'business_name'
        )

        # Validate required fields
        if not email:
            messages.error(request, 'Email wajib diisi.')
            return render(request, 'core/pages/register.html')

        if not password1 or password1 != password2:
            messages.error(request, 'Password tidak sama atau belum diisi.')
            return render(request, 'core/pages/register.html')

        if not restaurant_name:
            messages.error(request, 'Nama restoran wajib diisi.')
            return render(request, 'core/pages/register.html')

        # Check email uniqueness
        if User.objects.filter(email__iexact=email).exists():
            messages.error(
                request, 'Email sudah terdaftar. Silakan login atau gunakan email lain.'
            )
            return render(request, 'core/pages/register.html')

        # Auto-generate unique username from email prefix + random suffix
        base_username = slugify(email.split('@')[0]).replace('-', '_') or 'owner'
        username = f'{base_username}_{uuid.uuid4().hex[:6]}'
        while User.objects.filter(username=username).exists():
            username = f'{base_username}_{uuid.uuid4().hex[:6]}'

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_staff=True,
        )
        restaurant, _ = Restaurant.objects.get_or_create(
            slug=_unique_restaurant_slug(restaurant_name),
            defaults={'name': restaurant_name, 'is_active': True},
        )
        UserProfile.objects.create(
            user=user,
            restaurant=restaurant,
            role=Role.OWNER,
        )
        auth_login(request, user, backend='accounts.backends.EmailBackend')
        return redirect('dashboard')

    return render(request, 'core/pages/register.html')


def logout(request):
    auth_logout(request)
    return redirect('login')


def _unique_restaurant_slug(name):
    base_slug = slugify(name) or 'restaurant'
    slug = base_slug
    counter = 1
    while Restaurant.objects.filter(slug=slug).exists():
        counter += 1
        slug = f'{base_slug}-{counter}'
    return slug


# ─── Onboarding Wizard ────────────────────────────────────────────────────────


def _onboarding_guard(request):
    """Return redirect if user should not be in onboarding (already has restaurant)."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    try:
        profile = request.user.profile
        if profile.restaurant_id:
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        pass
    return None


@login_required(login_url='login')
def onboarding_step1(request):
    """Step 1 — Profil Toko: nama (required), deskripsi, telepon, logo (optional)."""
    guard = _onboarding_guard(request)
    if guard:
        return guard

    if request.method == 'POST':
        name = request.POST.get('restaurant_name', '').strip()
        if not name:
            messages.error(request, 'Nama restoran wajib diisi.')
            return render(request, 'core/pages/onboarding-step1.html')

        description = request.POST.get('description', '').strip()
        phone = request.POST.get('phone', '').strip()
        logo = request.FILES.get('logo')

        restaurant = Restaurant.objects.create(
            name=name,
            slug=_unique_restaurant_slug(name),
            description=description,
            phone=phone,
            is_active=True,
        )
        if logo:
            restaurant.logo = logo
            restaurant.save(update_fields=['logo'])

        # Link restaurant to UserProfile
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'role': Role.OWNER},
        )
        profile.restaurant = restaurant
        profile.save(update_fields=['restaurant'])

        return redirect('onboarding_step2')

    return render(request, 'core/pages/onboarding-step1.html')


@login_required(login_url='login')
def onboarding_step2(request):
    """Step 2 — Pallet Warna: choose from 10 presets (skippable)."""
    # Guard: must have completed step 1
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    try:
        profile = request.user.profile
        if not profile.restaurant_id:
            return redirect('onboarding_step1')
    except UserProfile.DoesNotExist:
        return redirect('onboarding_step1')

    if request.method == 'POST':
        palette_id = request.POST.get('palette_id', 'tapmenu')
        palette = next(
            (p for p in PALETTE_PRESETS if p['id'] == palette_id), PALETTE_PRESETS[0]
        )

        theme, _ = MenuAppearanceTheme.objects.get_or_create(
            restaurant=profile.restaurant,
        )
        theme.primary_color = palette['primary']
        theme.secondary_color = palette['secondary']
        theme.accent_color = palette['accent']
        theme.background_color = palette['bg']
        theme.card_color = palette['card']
        theme.save(
            update_fields=[
                'primary_color',
                'secondary_color',
                'accent_color',
                'background_color',
                'card_color',
            ]
        )

        return redirect('onboarding_step3')

    return render(
        request,
        'core/pages/onboarding-step2.html',
        {
            'palettes': PALETTE_PRESETS,
        },
    )


@login_required(login_url='login')
def onboarding_step3(request):
    """Step 3 — Tambah Karyawan (skippable)."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    try:
        profile = request.user.profile
        if not profile.restaurant_id:
            return redirect('onboarding_step1')
    except UserProfile.DoesNotExist:
        return redirect('onboarding_step1')

    if request.method == 'POST':
        action = request.POST.get('action', 'finish')

        if action == 'add_employee':
            email = request.POST.get('email', '').strip().lower()
            role = request.POST.get('role', 'kasir')
            emp_password = request.POST.get('password', '').strip()

            if email and emp_password:
                if User.objects.filter(email__iexact=email).exists():
                    messages.error(request, f'Email {email} sudah digunakan.')
                else:
                    restaurant_slug = profile.restaurant.slug
                    emp_username = f'{restaurant_slug}_{role}_{uuid.uuid4().hex[:6]}'
                    emp_user = User.objects.create_user(
                        username=emp_username,
                        email=email,
                        password=emp_password,
                        is_staff=True,
                    )
                    UserProfile.objects.create(
                        user=emp_user,
                        restaurant=profile.restaurant,
                        role=role,
                    )
                    messages.success(request, f'Karyawan {email} berhasil ditambahkan.')
            return redirect('onboarding_step3')

        # action == 'finish' or 'skip'
        messages.success(request, '__onboarding_complete__')
        return redirect('dashboard')

    return render(
        request,
        'core/pages/onboarding-step3.html',
        {
            'role_choices': [
                ('admin', 'Admin'),
                ('kasir', 'Kasir'),
                ('dapur', 'Dapur'),
            ],
        },
    )
