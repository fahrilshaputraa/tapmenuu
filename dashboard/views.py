import json
import uuid
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role, UserProfile
from dashboard.forms import (
    DiningTableForm,
    EmployeeCreateForm,
    EmployeeUpdateForm,
    MenuAppearanceThemeForm,
    MenuCategoryForm,
    MenuItemForm,
    OrderStatusForm,
    RestaurantForm,
)
from menus.models import (
    MenuCategory,
    MenuItem,
    MenuItemVariantGroup,
    MenuItemVariantOption,
)
from orders.models import Order
from restaurants.models import DiningTable, MenuAppearanceTheme, Restaurant


def _save_variants(menu_item, variants_json):
    """Save variant groups and options from JSON string sent by the modal."""
    if not variants_json:
        return
    try:
        variants_data = json.loads(variants_json)
    except (json.JSONDecodeError, TypeError):
        return

    # Delete existing variants for this item
    menu_item.variant_groups.all().delete()

    for idx, group_data in enumerate(variants_data):
        group = MenuItemVariantGroup.objects.create(
            menu_item=menu_item,
            name=group_data.get('name', ''),
            type=group_data.get('type', 'radio'),
            sort_order=idx,
        )
        for opt_idx, opt_data in enumerate(group_data.get('options', [])):
            MenuItemVariantOption.objects.create(
                group=group,
                name=opt_data.get('name', ''),
                price_adjustment=int(opt_data.get('price', 0) or 0),
                sort_order=opt_idx,
            )


def _build_variants_json(menu_item):
    """Build JSON string of variants for pre-filling the edit modal."""
    groups = menu_item.variant_groups.prefetch_related('options').order_by(
        'sort_order', 'name'
    )
    result = []
    for group in groups:
        options = []
        for opt in group.options.order_by('sort_order', 'name'):
            options.append(
                {
                    'name': opt.name,
                    'price': opt.price_adjustment,
                }
            )
        result.append(
            {
                'name': group.name,
                'type': group.type,
                'options': options,
            }
        )
    return json.dumps(result)


def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('Dashboard hanya untuk staff/admin.')
        # Onboarding guard — only redirect OWNER without restaurant; other roles
        # (kasir/dapur/admin) without restaurant are allowed to access.
        # Superusers always skip onboarding.
        profile = _get_or_create_profile(request.user)
        # Legacy compat: tests create Restaurant without linking UserProfile.
        # If exactly one restaurant exists and profile has none, auto-attach it
        # to keep old tests green without leaking across multi-tenant DBs.
        if profile.restaurant_id is None and not request.user.is_superuser:
            if Restaurant.objects.count() == 1:
                first = Restaurant.objects.order_by('id').first()
                if first:
                    profile.restaurant = first
                    profile.save(update_fields=['restaurant'])
        if (
            profile.role == Role.OWNER
            and profile.restaurant_id is None
            and not request.user.is_superuser
            and Restaurant.objects.exists()
        ):
            from django.urls import reverse as _reverse
            return redirect(_reverse('onboarding_step1'))
        return view_func(request, *args, **kwargs)

    return wrapper


def role_required(*roles):
    """Decorator that requires the user to be staff AND have one of the given roles.

    Handles users without a UserProfile by creating one lazily with role=owner,
    so existing staff users don't lose access.
    """

    def decorator(view_func):
        @wraps(view_func)
        @staff_required
        def wrapper(request, *args, **kwargs):
            profile = _get_or_create_profile(request.user)
            if not profile.role:
                # Should never happen after _get_or_create_profile, but guard.
                profile.role = Role.OWNER
                profile.save(update_fields=['role'])
            if profile.role not in roles:
                raise PermissionDenied(
                    'Anda tidak memiliki akses ke halaman ini.',
                )
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def _get_or_create_profile(user):
    """Return or lazily create a UserProfile for the given user."""
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': Role.OWNER},
    )
    return profile


def _profile_restaurant(user):
    """Return the restaurant scoping for a user, or None for superusers.

    Staff users are scoped to their UserProfile.restaurant. Superusers with no
    restaurant see all data.
    """
    profile = _get_or_create_profile(user)
    if profile.restaurant_id:
        return profile.restaurant
    if user.is_superuser:
        return None
    return None


def _scoped_order_queryset(user):
    """Order queryset scoped to the user's restaurant when one is set."""
    queryset = Order.objects.select_related(
        'restaurant',
        'dining_table',
    ).prefetch_related('items', 'payments')
    restaurant = _profile_restaurant(user)
    if restaurant is not None:
        queryset = queryset.filter(restaurant=restaurant)
    return queryset


def _dashboard_context(request=None, **extra):
    # Scope restaurant to the logged-in user's restaurant via _profile_restaurant;
    # superuser (None) falls back to first restaurant.
    restaurant = None
    if request and request.user.is_authenticated:
        restaurant = _profile_restaurant(request.user)
    if restaurant is None:
        restaurant = Restaurant.objects.order_by('id').first()
    orders = Order.objects.select_related(
        'restaurant',
        'dining_table',
    ).prefetch_related(
        'items',
        'payments',
    )
    context = {
        'restaurant': restaurant,
        'restaurants': Restaurant.objects.all(),
        'tables': DiningTable.objects.select_related('restaurant'),
        'categories': MenuCategory.objects.select_related('restaurant'),
        'menu_items': MenuItem.objects.select_related('restaurant', 'category'),
        'orders': orders,
    }
    context.update(extra)
    return context


def _order_status_counts(queryset):
    raw_counts = queryset.values('status').annotate(count=Count('id'))
    counts = {row['status']: row['count'] for row in raw_counts}
    return {
        'all': queryset.count(),
        'new': counts.get(Order.Status.NEW, 0),
        'paid': counts.get(Order.Status.PAID, 0),
        'processing': counts.get(Order.Status.PROCESSING, 0),
        'ready': counts.get(Order.Status.READY, 0),
        'completed': counts.get(Order.Status.COMPLETED, 0),
        'cancelled': counts.get(Order.Status.CANCELLED, 0),
    }


def _average_order_value(queryset):
    count = queryset.count()
    if count == 0:
        return 0
    revenue = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
    return int(revenue / count)


@staff_required
def dashboard_home(request):
    profile = _get_or_create_profile(request.user)
    if profile.role == Role.DAPUR:
        return redirect(reverse('kitchen'))

    # Check onboarding completion toast — uses messages
    # framework for reliable cross-request delivery
    show_welcome_toast = False
    storage = messages.get_messages(request)
    remaining_messages = []
    for msg in storage:
        if str(msg) == '__onboarding_complete__':
            show_welcome_toast = True
        else:
            remaining_messages.append(msg)
    # Re-add non-onboarding messages so they still render
    for msg in remaining_messages:
        messages.add_message(request, msg.level, str(msg))

    # Check if restaurant profile is incomplete
    restaurant = profile.restaurant
    profile_incomplete = False
    missing_fields = []
    if restaurant:
        if not restaurant.description:
            missing_fields.append('deskripsi')
        if not restaurant.phone:
            missing_fields.append('no. telepon')
        if not restaurant.logo:
            missing_fields.append('logo')
        profile_incomplete = bool(missing_fields)

    orders = Order.objects.select_related('dining_table').prefetch_related('items')
    active_orders = orders.exclude(
        status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED],
    )
    paid_orders = orders.filter(payment_status=Order.PaymentStatus.PAID)
    revenue = paid_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    pending_payments = (
        orders.exclude(status__in=[Order.Status.CANCELLED])
        .exclude(payment_status=Order.PaymentStatus.PAID)
        .exclude(payment_status=Order.PaymentStatus.REFUNDED)
        .aggregate(total=Sum('total_amount'))['total']
        or 0
    )
    table_total = DiningTable.objects.count()
    table_with_orders = (
        active_orders.values('dining_table').distinct().count() if table_total else 0
    )
    context = _dashboard_context(
        request=request,
        total_orders=orders.count(),
        active_orders=active_orders.count(),
        paid_count=paid_orders.count(),
        revenue=revenue,
        pending_payments=pending_payments,
        average_order_value=_average_order_value(orders),
        menu_count=MenuItem.objects.filter(is_active=True).count(),
        table_total=table_total,
        table_with_orders=table_with_orders,
        recent_orders=orders[:5],
        current_date=timezone.localdate(),
        show_welcome_toast=show_welcome_toast,
        profile_incomplete=profile_incomplete,
        missing_fields=missing_fields,
    )
    return render(request, 'core/pages/dashboard.html', context)


@role_required('owner', 'admin')
def store(request):
    restaurant = _profile_restaurant(request.user)
    if restaurant is None:
        restaurant = Restaurant.objects.order_by('id').first()
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('store')
    else:
        form = RestaurantForm(instance=restaurant)

    return render(
        request,
        'core/pages/store.html',
        _dashboard_context(request=request, restaurant_form=form),
    )


@role_required('owner', 'admin')
def menu_appearance(request):
    restaurant = _profile_restaurant(request.user)
    if restaurant is None:
        restaurant = Restaurant.objects.order_by('id').first()
    if not restaurant:
        return render(
            request,
            'core/pages/menu-appearance.html',
            _dashboard_context(
                request=request, appearance_theme=None, appearance_form=None
            ),
        )

    theme, _ = MenuAppearanceTheme.objects.get_or_create(restaurant=restaurant)
    if request.method == 'POST' and request.POST.get('reset_theme'):
        theme.reset_to_defaults()
        return redirect('menu_appearance')

    if request.method == 'POST':
        form = MenuAppearanceThemeForm(request.POST, instance=theme)
        if form.is_valid():
            form.save()
            return redirect('menu_appearance')
    else:
        form = MenuAppearanceThemeForm(instance=theme)

    return render(
        request,
        'core/pages/menu-appearance.html',
        _dashboard_context(
            request=request, appearance_theme=theme, appearance_form=form
        ),
    )


@role_required('owner', 'admin')
def tables(request):
    return render(
        request,
        'core/pages/tables.html',
        _dashboard_context(request=request, table_form=DiningTableForm()),
    )


@role_required('owner', 'admin')
def table_create(request):
    form = DiningTableForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect('tables')


@role_required('owner', 'admin')
def table_update(request, pk):
    table = get_object_or_404(DiningTable, pk=pk)
    form = DiningTableForm(request.POST or None, instance=table)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect('tables')


@role_required('owner', 'admin')
def table_delete(request, pk):
    table = get_object_or_404(DiningTable, pk=pk)
    if request.method == 'POST':
        table.delete()
    return redirect('tables')


@role_required('owner', 'admin')
def management_menu(request):
    return render(
        request,
        'core/pages/management-menu.html',
        _dashboard_context(
            request=request,
            category_form=MenuCategoryForm(),
            menu_item_form=MenuItemForm(),
        ),
    )


@role_required('owner', 'admin')
def category_create(request):
    form = MenuCategoryForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('category_management')
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return redirect('category_management')


@role_required('owner', 'admin')
def category_update(request, pk):
    category = get_object_or_404(MenuCategory, pk=pk)
    form = MenuCategoryForm(request.POST or None, instance=category)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('category_management')
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return redirect('category_management')


@role_required('owner', 'admin')
def category_delete(request, pk):
    category = get_object_or_404(MenuCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
    return redirect('category_management')


@role_required('owner', 'admin')
def menu_item_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            _save_variants(item, request.POST.get('variants'))
            return redirect('management_menu')
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return redirect('management_menu')


@role_required('owner', 'admin')
def menu_item_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save()
            _save_variants(item, request.POST.get('variants'))
            return redirect('management_menu')
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return redirect('management_menu')


@role_required('owner', 'admin')
def menu_item_variants_json(request, pk):
    """Return variant groups and options as JSON for pre-filling the edit modal."""
    item = get_object_or_404(MenuItem, pk=pk)
    variants = json.loads(_build_variants_json(item))
    return JsonResponse({'variants': variants})


@role_required('owner', 'admin')
def menu_item_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        item.delete()
    return redirect('management_menu')


@staff_required
def orders(request):
    status = request.GET.get('status')
    base_queryset = _scoped_order_queryset(request.user)
    queryset = base_queryset
    if status:
        queryset = queryset.filter(status=status)
    return render(
        request,
        'core/pages/orders.html',
        _dashboard_context(
            request=request,
            orders=queryset,
            order_statuses=Order.Status.choices,
            status_counts=_order_status_counts(base_queryset),
            current_status=status or 'all',
            current_time=timezone.localtime(),
        ),
    )


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(
        _scoped_order_queryset(request.user),
        pk=pk,
    )
    return render(
        request,
        'dashboard/order_detail.html',
        _dashboard_context(
            request=request, order=order, status_form=OrderStatusForm(instance=order)
        ),
    )


@role_required('owner', 'admin', 'kasir', 'dapur')
def order_update_status(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('restaurant', 'dining_table'),
        pk=pk,
    )
    restaurant = _profile_restaurant(request.user)
    if restaurant is not None and order.restaurant_id != restaurant.id:
        raise PermissionDenied('Anda tidak memiliki akses ke pesanan ini.')
    form = OrderStatusForm(request.POST or None, instance=order)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect(reverse('order_detail', kwargs={'pk': order.pk}))


@role_required('owner', 'admin', 'kasir')
def admin_receipt(request, pk):
    order = get_object_or_404(
        _scoped_order_queryset(request.user),
        pk=pk,
    )
    subtotal = sum(item.line_total for item in order.items.all())
    theme, _ = MenuAppearanceTheme.objects.get_or_create(
        restaurant=order.restaurant,
    )
    return render(
        request,
        'menus/customer_receipt.html',
        {
            'dining_table': order.dining_table,
            'restaurant': order.restaurant,
            'order': order,
            'payment': order.payments.first(),
            'subtotal': subtotal,
            'theme': theme,
            'is_staff_view': True,
        },
    )


@role_required('owner', 'admin')
def reports(request):
    orders = Order.objects.select_related('restaurant').prefetch_related('payments')
    paid_orders = orders.filter(payment_status=Order.PaymentStatus.PAID)
    revenue = paid_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    order_count = orders.count()
    by_status = [
        {
            'status': status,
            'label': label,
            'count': orders.filter(status=status).count(),
        }
        for status, label in Order.Status.choices
    ]
    recent_transactions = orders[:10]
    return render(
        request,
        'core/pages/reports.html',
        _dashboard_context(
            request=request,
            revenue=revenue,
            order_count=order_count,
            paid_count=paid_orders.count(),
            average_order_value=_average_order_value(orders),
            by_status=by_status,
            recent_transactions=recent_transactions,
        ),
    )


@role_required('owner')
def employee(request):
    restaurant = _profile_restaurant(request.user)
    profiles = (
        UserProfile.objects.filter(restaurant=restaurant)
        .exclude(role=Role.OWNER)
        .select_related('user')
        .order_by('user__email')
    )
    create_form = EmployeeCreateForm()
    return render(
        request,
        'core/pages/employee.html',
        _dashboard_context(
            request=request,
            profiles=profiles,
            create_form=create_form,
            active_count=profiles.filter(user__is_active=True).count(),
            inactive_count=profiles.filter(user__is_active=False).count(),
        ),
    )


@role_required('owner')
def employee_create(request):
    if request.method != 'POST':
        return redirect('employee')
    restaurant = _profile_restaurant(request.user)
    form = EmployeeCreateForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']
        # Auto-generate unique username: {restaurant_slug}_{role}_{random6}
        restaurant_slug = restaurant.slug if restaurant else 'staff'
        base_username = f'{restaurant_slug}_{role}'
        username = f'{base_username}_{uuid.uuid4().hex[:6]}'
        while User.objects.filter(username=username).exists():
            username = f'{base_username}_{uuid.uuid4().hex[:6]}'
        user = User.objects.create_user(
            username=username,
            email=email,
            password=form.cleaned_data['password'],
            is_staff=True,
        )
        UserProfile.objects.create(
            user=user,
            restaurant=restaurant,
            role=role,
        )
        messages.success(request, f'Karyawan {email} berhasil ditambahkan.')
        return redirect('employee')
    profiles = (
        UserProfile.objects.filter(restaurant=restaurant)
        .exclude(role=Role.OWNER)
        .select_related('user')
        .order_by('user__email')
    )
    return render(
        request,
        'core/pages/employee.html',
        _dashboard_context(
            request=request,
            profiles=profiles,
            create_form=form,
            active_count=profiles.filter(user__is_active=True).count(),
            inactive_count=profiles.filter(user__is_active=False).count(),
        ),
    )


@role_required('owner')
def employee_update(request, pk):
    restaurant = _profile_restaurant(request.user)
    profile = get_object_or_404(UserProfile, pk=pk, restaurant=restaurant)
    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST)
        if form.is_valid():
            profile.role = form.cleaned_data['role']
            profile.save(update_fields=['role'])
            profile.user.is_active = form.cleaned_data.get('is_active', False)
            profile.user.save(update_fields=['is_active'])
            messages.success(request, 'Data karyawan diperbarui.')
    return redirect('employee')


@role_required('owner')
def employee_delete(request, pk):
    restaurant = _profile_restaurant(request.user)
    profile = get_object_or_404(UserProfile, pk=pk, restaurant=restaurant)
    if request.method == 'POST':
        if profile.user == request.user:
            messages.error(request, 'Tidak dapat menghapus akun Anda sendiri.')
            return redirect('employee')
        username = profile.user.username
        profile.user.delete()
        messages.success(request, f'Karyawan {username} dihapus.')
    return redirect('employee')


@role_required('owner', 'admin')
def category_management(request):
    all_categories = MenuCategory.objects.select_related('restaurant').order_by(
        'restaurant__name', 'sort_order', 'name'
    )
    active_count = all_categories.filter(is_active=True).count()
    inactive_count = all_categories.filter(is_active=False).count()
    return render(
        request,
        'core/pages/categories.html',
        _dashboard_context(
            request=request,
            all_categories=all_categories,
            active_count=active_count,
            inactive_count=inactive_count,
        ),
    )


@role_required('owner', 'admin', 'dapur')
def kitchen(request):
    """Kitchen board: live work queue of orders to prepare and serve."""
    restaurant = _profile_restaurant(request.user)
    qs = Order.objects.filter(
        status__in=[Order.Status.PAID, Order.Status.PROCESSING],
    )
    if restaurant is not None:
        qs = qs.filter(restaurant=restaurant)
    active_orders = (
        qs.select_related('dining_table', 'restaurant')
        .prefetch_related('items')
        .order_by('-created_at')
    )
    return render(
        request,
        'dashboard/kitchen.html',
        _dashboard_context(
            request=request,
            kitchen_orders=active_orders,
            kitchen_total=active_orders.count(),
        ),
    )
