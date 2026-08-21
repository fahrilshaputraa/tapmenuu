import json
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from payments.gateways.midtrans import MidtransError, MidtransPaymentGateway
from payments.models import Payment


def payment_staff_required(view_func):
    """Require a logged-in staff user with a payment-handling role."""

    @login_required
    @require_POST
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from accounts.models import Role, UserProfile

        try:
            profile = request.user.profile
            role = profile.role
            profile_restaurant_id = profile.restaurant_id
        except (UserProfile.DoesNotExist, AttributeError):
            role = None
            profile_restaurant_id = None
        if role not in (Role.OWNER, Role.ADMIN, Role.KASIR):
            raise PermissionDenied('Tidak memiliki akses pembayaran.')
        # Scope check: staff can only act on payments belonging to their restaurant.
        if profile_restaurant_id is not None and 'reference' in kwargs:
            payment = get_object_or_404(
                Payment.objects.select_related('order'),
                reference=kwargs['reference'],
            )
            if payment.order.restaurant_id != profile_restaurant_id:
                raise PermissionDenied('Akses pembayaran ditolak untuk restoran lain.')
        return view_func(request, *args, **kwargs)

    return wrapper


@payment_staff_required
def dummy_success(request, reference):
    payment = get_object_or_404(
        Payment.objects.select_related('order'),
        reference=reference,
    )
    payment.mark_paid()
    return redirect('order_detail', pk=payment.order.pk)


@csrf_exempt
@require_POST
def webhook(request):
    """Webhook endpoint for payment provider notifications.

    - Midtrans notifications are verified (signature + status mapping) via the
      Midtrans gateway.
    - A generic payload with ``reference`` + ``status`` is accepted for
      development/testing (dummy gateway) ONLY when a shared secret is set in
      ``PAYMENT_WEBHOOK_SECRET`` and the request carries it in the
      ``Authorization`` header. When Midtrans is configured, the generic branch
      is disabled entirely.
    """
    try:
        payload = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        payload = request.POST

    # Midtrans sends order_id + signature_key instead of reference.
    if 'signature_key' in payload or payload.get('order_id'):
        try:
            verified = MidtransPaymentGateway().verify_callback(payload)
        except MidtransError as exc:
            return JsonResponse({'status': 'error', 'reason': str(exc)}, status=400)

        payment = get_object_or_404(
            Payment.objects.select_related('order'),
            reference=verified['reference'],
        )
        new_status = verified['status']
        if new_status == Payment.Status.PAID:
            payment.mark_paid()
        elif new_status != payment.status:
            payment.status = new_status
            payment.save(update_fields=['status', 'updated_at'])
        return JsonResponse({'status': 'ok', 'reference': payment.reference})

    reference = payload.get('reference')
    status = payload.get('status')

    # When Midtrans is configured, the generic (dummy) webhook is disabled
    # entirely — even with a valid PAYMENT_WEBHOOK_SECRET. This prevents
    # unsigned generic payloads from mutating payments in production.
    if settings.MIDTRANS_SERVER_KEY and settings.MIDTRANS_CLIENT_KEY:
        return JsonResponse(
            {
                'status': 'ignored',
                'reason': 'generic webhook disabled when midtrans configured',
            },
            status=403,
        )

    # Generic (non-Midtrans) notifications are only allowed in development
    # when a shared secret is configured and provided.
    if not settings.PAYMENT_WEBHOOK_SECRET:
        return JsonResponse(
            {'status': 'ignored', 'reason': 'generic webhook disabled'},
            status=403,
        )
    auth_header = request.headers.get('Authorization', '')
    if auth_header != f'Bearer {settings.PAYMENT_WEBHOOK_SECRET}':
        return JsonResponse(
            {'status': 'error', 'reason': 'invalid webhook secret'},
            status=401,
        )

    if not reference:
        return JsonResponse(
            {'status': 'ignored', 'reason': 'missing reference'},
            status=400,
        )

    payment = get_object_or_404(
        Payment.objects.select_related('order'),
        reference=reference,
    )
    if status == 'paid':
        payment.mark_paid()
    elif status in Payment.Status.values:
        payment.status = status
        payment.save(update_fields=['status', 'updated_at'])

    return JsonResponse({'status': 'ok', 'reference': payment.reference})
