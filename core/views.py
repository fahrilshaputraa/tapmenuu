from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from django.db.models import Prefetch

from menus.models import MenuCategory, MenuItem
from menus.views import _build_cart_summary
from restaurants.models import DiningTable
from restaurants.models import Restaurant


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
        username = (
            request.POST.get('username')
            or request.POST.get('email')
            or request.POST.get('fullname')
            or 'owner'
        )
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1') or request.POST.get('password')
        password2 = request.POST.get('password2') or request.POST.get(
            'confirm_password',
        )
        restaurant_name = request.POST.get('restaurant_name') or request.POST.get(
            'business_name',
        )

        if password1 and password1 == password2 and restaurant_name:
            base_username = slugify(username).replace('-', '_') or 'owner'
            final_username = base_username
            counter = 1
            while User.objects.filter(username=final_username).exists():
                counter += 1
                final_username = f'{base_username}_{counter}'

            user = User.objects.create_user(
                username=final_username,
                email=email,
                password=password1,
                is_staff=True,
            )
            Restaurant.objects.get_or_create(
                slug=_unique_restaurant_slug(restaurant_name),
                defaults={'name': restaurant_name, 'is_active': True},
            )
            auth_login(request, user)
            return redirect('dashboard')

        messages.error(
            request,
            'Data pendaftaran belum lengkap atau password tidak sama.',
        )

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
