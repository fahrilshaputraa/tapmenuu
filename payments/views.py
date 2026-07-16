import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from payments.models import Payment


@login_required
@require_POST
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
    try:
        payload = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        payload = request.POST

    reference = payload.get('reference')
    status = payload.get('status')
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
