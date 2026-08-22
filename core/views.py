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

# 18 color palette presets — kombinasi warna terkurasi
# Categories: natural / hangat / sejuk / vibrant / soft / netral
# Each palette maps to MenuAppearanceTheme: primary/secondary/accent/bg/card/text
PALETTE_PRESETS = [
    {
        'id': 'tapmenu',
        'name': 'TapMenu',
        'description': 'Hijau alami • Lush Forest',
        'category': 'Natural',
        'primary': '#1B4332',
        'secondary': '#D8F3DC',
        'accent': '#E07A5F',
        'bg': '#F7F5F2',
        'card': '#FFFFFF',
        'text': '#1F2933',
    },
    {
        'id': 'kopi',
        'name': 'Kopi Susu',
        'description': 'Cappuccino • Chocolate Truffle',
        'category': 'Hangat',
        'primary': '#4A271A',
        'secondary': '#FDE68A',
        'accent': '#EA580C',
        'bg': '#FFFBEB',
        'card': '#FFF7ED',
        'text': '#1C1917',
    },
    {
        'id': 'ocean',
        'name': 'Ocean',
        'description': 'Blue Eclipse • Harbor Haze',
        'category': 'Sejuk',
        'primary': '#0F2A44',
        'secondary': '#BFDBFE',
        'accent': '#0EA5E9',
        'bg': '#EFF6FF',
        'card': '#FFFFFF',
        'text': '#0F172A',
    },
    {
        'id': 'matcha',
        'name': 'Matcha',
        'description': 'Pistachio Dream • Green Juice',
        'category': 'Natural',
        'primary': '#14532D',
        'secondary': '#BBF7D0',
        'accent': '#16A34A',
        'bg': '#F0FDF4',
        'card': '#FFFFFF',
        'text': '#052E16',
    },
    {
        'id': 'sunset',
        'name': 'Sunset Terracotta',
        'description': 'Tuscan Sunset • Golden Hour',
        'category': 'Hangat',
        'primary': '#9A3412',
        'secondary': '#FFEDD5',
        'accent': '#F97316',
        'bg': '#FFF7ED',
        'card': '#FFFFFF',
        'text': '#431407',
    },
    {
        'id': 'lavender',
        'name': 'Lavender',
        'description': 'Wisteria Bloom • Iris Garden',
        'category': 'Soft',
        'primary': '#4C1D95',
        'secondary': '#DDD6FE',
        'accent': '#8B5CF6',
        'bg': '#F5F3FF',
        'card': '#FFFFFF',
        'text': '#1E1B4B',
    },
    {
        'id': 'chili',
        'name': 'Chili',
        'description': 'Chili Spice • Alchemical',
        'category': 'Vibrant',
        'primary': '#7F1D1D',
        'secondary': '#FECACA',
        'accent': '#DC2626',
        'bg': '#FEF2F2',
        'card': '#FFFFFF',
        'text': '#450A0A',
    },
    {
        'id': 'midnight',
        'name': 'Midnight',
        'description': 'Blue Eclipse • Neon Noir',
        'category': 'Soft',
        'primary': '#1E1B4B',
        'secondary': '#C7D2FE',
        'accent': '#6366F1',
        'bg': '#EEF2FF',
        'card': '#FFFFFF',
        'text': '#1E1B4B',
    },
    {
        'id': 'mint',
        'name': 'Mint Teal',
        'description': 'Eucalyptus • Morning Dew',
        'category': 'Sejuk',
        'primary': '#134E4A',
        'secondary': '#99F6E4',
        'accent': '#14B8A6',
        'bg': '#F0FDFA',
        'card': '#FFFFFF',
        'text': '#042F2E',
    },
    {
        'id': 'honey',
        'name': 'Honey',
        'description': 'Honeycomb • Spiced Chai',
        'category': 'Hangat',
        'primary': '#78350F',
        'secondary': '#FDE68A',
        'accent': '#F59E0B',
        'bg': '#FFFBEB',
        'card': '#FFF7ED',
        'text': '#431407',
    },
    {
        'id': 'berry',
        'name': 'Berry',
        'description': 'Cherry Blossom • Evening Rose',
        'category': 'Vibrant',
        'primary': '#831843',
        'secondary': '#FBCFE8',
        'accent': '#EC4899',
        'bg': '#FDF2F8',
        'card': '#FFFFFF',
        'text': '#4A044E',
    },
    {
        'id': 'stone',
        'name': 'Stone',
        'description': 'Quiet Luxury • Stone Path',
        'category': 'Netral',
        'primary': '#292524',
        'secondary': '#E7E5E4',
        'accent': '#D97706',
        'bg': '#FAFAF9',
        'card': '#FFFFFF',
        'text': '#1C1917',
    },
    {
        'id': 'coral',
        'name': 'Coral',
        'description': 'Watermelon Splash • Guava',
        'category': 'Vibrant',
        'primary': '#9F1239',
        'secondary': '#FFE4E6',
        'accent': '#E11D48',
        'bg': '#FFF1F2',
        'card': '#FFFFFF',
        'text': '#4C0519',
    },
    {
        'id': 'olive',
        'name': 'Olive',
        'description': 'Mossy Hollow • Olive Grove',
        'category': 'Natural',
        'primary': '#365314',
        'secondary': '#D9F99D',
        'accent': '#65A30D',
        'bg': '#F7FEE7',
        'card': '#FFFFFF',
        'text': '#1A2E05',
    },
    {
        'id': 'slate',
        'name': 'Slate Harbor',
        'description': 'Stormy Morning • Siltstone',
        'category': 'Netral',
        'primary': '#1E293B',
        'secondary': '#E2E8F0',
        'accent': '#64748B',
        'bg': '#F8FAFC',
        'card': '#FFFFFF',
        'text': '#0F172A',
    },
    {
        'id': 'peach',
        'name': 'Peach Dusk',
        'description': 'Fresh Peach • Desert Dusk',
        'category': 'Hangat',
        'primary': '#7C2D12',
        'secondary': '#FFEDD5',
        'accent': '#FB923C',
        'bg': '#FFF7ED',
        'card': '#FFFBEB',
        'text': '#431407',
    },
    {
        'id': 'cyber',
        'name': 'Cyber',
        'description': 'Neon Jungle • Electropop',
        'category': 'Vibrant',
        'primary': '#312E81',
        'secondary': '#A5B4FC',
        'accent': '#06B6D4',
        'bg': '#EEF2FF',
        'card': '#FFFFFF',
        'text': '#1E1B4B',
    },
    {
        'id': 'emerald',
        'name': 'Emerald Night',
        'description': 'Emerald Odyssey • Coastal',
        'category': 'Sejuk',
        'primary': '#064E3B',
        'secondary': '#6EE7B7',
        'accent': '#10B981',
        'bg': '#ECFDF5',
        'card': '#FFFFFF',
        'text': '#022C22',
    },
]


def page(template_name):
    def view(request):
        return render(request, f'core/pages/{template_name}')

    return view


landing = page('landing.html')


def book_menu(request):
    # Scoped to logged-in user's restaurant when possible (fix F&B sebelah leak)
    restaurant = None
    if request.user.is_authenticated and request.user.is_staff:
        try:
            profile = request.user.profile
            if profile.restaurant_id:
                restaurant = profile.restaurant
        except UserProfile.DoesNotExist:
            pass
    if restaurant is None:
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
    """Step 2 — Pallet Warna: choose from 18 presets (skippable)."""
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
        theme.text_color = palette.get('text', '#1F2933')
        theme.save(
            update_fields=[
                'primary_color',
                'secondary_color',
                'accent_color',
                'background_color',
                'card_color',
                'text_color',
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
