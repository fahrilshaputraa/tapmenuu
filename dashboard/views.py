from functools import wraps
import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from dashboard.forms import (
    DiningTableForm,
    MenuAppearanceThemeForm,
    MenuCategoryForm,
    MenuItemForm,
    OrderStatusForm,
    RestaurantForm,
)
from menus.models import MenuCategory, MenuItem, MenuItemVariantGroup, MenuItemVariantOption
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
    groups = menu_item.variant_groups.prefetch_related('options').order_by('sort_order', 'name')
    result = []
    for group in groups:
        options = []
        for opt in group.options.order_by('sort_order', 'name'):
            options.append({
                'name': opt.name,
                'price': opt.price_adjustment,
            })
        result.append({
            'name': group.name,
            'type': group.type,
            'options': options,
        })
    return json.dumps(result)


def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('Dashboard hanya untuk staff/admin.')
        return view_func(request, *args, **kwargs)

    return wrapper


def _dashboard_context(**extra):
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
        'pending': counts.get(Order.Status.PENDING, 0),
        'confirmed': counts.get(Order.Status.CONFIRMED, 0),
        'preparing': counts.get(Order.Status.PREPARING, 0),
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
    orders = Order.objects.select_related('dining_table').prefetch_related('items')
    active_orders = orders.exclude(
        status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED],
    )
    revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    table_total = DiningTable.objects.count()
    table_with_orders = (
        active_orders.values('dining_table').distinct().count() if table_total else 0
    )
    context = _dashboard_context(
        total_orders=orders.count(),
        active_orders=active_orders.count(),
        paid_count=orders.filter(payment_status=Order.PaymentStatus.PAID).count(),
        revenue=revenue,
        average_order_value=_average_order_value(orders),
        menu_count=MenuItem.objects.filter(is_active=True).count(),
        table_total=table_total,
        table_with_orders=table_with_orders,
        recent_orders=orders[:5],
        current_date=timezone.localdate(),
    )
    return render(request, 'core/pages/dashboard.html', context)


@staff_required
def store(request):
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
        _dashboard_context(restaurant_form=form),
    )


@staff_required
def menu_appearance(request):
    restaurant = Restaurant.objects.order_by('id').first()
    if not restaurant:
        return render(
            request,
            'core/pages/menu-appearance.html',
            _dashboard_context(appearance_theme=None, appearance_form=None),
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
        _dashboard_context(appearance_theme=theme, appearance_form=form),
    )


@staff_required
def tables(request):
    return render(
        request,
        'core/pages/tables.html',
        _dashboard_context(table_form=DiningTableForm()),
    )


@staff_required
def table_create(request):
    form = DiningTableForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect('tables')


@staff_required
def table_update(request, pk):
    table = get_object_or_404(DiningTable, pk=pk)
    form = DiningTableForm(request.POST or None, instance=table)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect('tables')


@staff_required
def table_delete(request, pk):
    table = get_object_or_404(DiningTable, pk=pk)
    if request.method == 'POST':
        table.delete()
    return redirect('tables')


@staff_required
def management_menu(request):
    return render(
        request,
        'core/pages/management-menu.html',
        _dashboard_context(
            category_form=MenuCategoryForm(),
            menu_item_form=MenuItemForm(),
        ),
    )


@staff_required
def category_create(request):
    form = MenuCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect('category_management')


@staff_required
def category_update(request, pk):
    category = get_object_or_404(MenuCategory, pk=pk)
    form = MenuCategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect('category_management')


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(MenuCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
    return redirect('category_management')


@staff_required
def menu_item_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            _save_variants(item, request.POST.get('variants'))
            return redirect('management_menu')
    return redirect('management_menu')


@staff_required
def menu_item_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save()
            _save_variants(item, request.POST.get('variants'))
            return redirect('management_menu')
    return redirect('management_menu')


@staff_required
def menu_item_variants_json(request, pk):
    """Return variant groups and options as JSON for pre-filling the edit modal."""
    item = get_object_or_404(MenuItem, pk=pk)
    variants = json.loads(_build_variants_json(item))
    return JsonResponse({'variants': variants})


@staff_required
def menu_item_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        item.delete()
    return redirect('management_menu')


@staff_required
def orders(request):
    status = request.GET.get('status')
    base_queryset = Order.objects.select_related(
        'restaurant',
        'dining_table',
    ).prefetch_related(
        'items',
        'payments',
    )
    queryset = base_queryset
    if status:
        queryset = queryset.filter(status=status)
    return render(
        request,
        'core/pages/orders.html',
        _dashboard_context(
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
        Order.objects.select_related('restaurant', 'dining_table').prefetch_related(
            'items',
            'payments',
        ),
        pk=pk,
    )
    return render(
        request,
        'dashboard/order_detail.html',
        _dashboard_context(order=order, status_form=OrderStatusForm(instance=order)),
    )


@staff_required
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    form = OrderStatusForm(request.POST or None, instance=order)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect(reverse('order_detail', kwargs={'pk': order.pk}))


@staff_required
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
            revenue=revenue,
            order_count=order_count,
            paid_count=paid_orders.count(),
            average_order_value=_average_order_value(orders),
            by_status=by_status,
            recent_transactions=recent_transactions,
        ),
    )


@staff_required
def employee(request):
    return render(request, 'core/pages/employee.html', _dashboard_context())


@staff_required
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
            all_categories=all_categories,
            active_count=active_count,
            inactive_count=inactive_count,
        ),
    )
