from django.db import models
from django.utils import timezone

from orders.models import Order


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        QRIS = 'qris', 'QRIS'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        EWALLET = 'ewallet', 'E-Wallet'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        EXPIRED = 'expired', 'Expired'
        REFUNDED = 'refunded', 'Refunded'

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    reference = models.CharField(max_length=60, unique=True)
    method = models.CharField(max_length=30, choices=Method.choices)
    amount = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    provider = models.CharField(max_length=80, blank=True)
    provider_reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} - {self.order.code}'

    def mark_paid(self):
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at', 'updated_at'])

        self.order.payment_status = Order.PaymentStatus.PAID
        # Persist payment_status first so it survives the status transition
        # save below (which only writes status/updated_at).
        self.order.save(update_fields=['payment_status', 'updated_at'])
        # Advance the order status through the state machine when it is still
        # waiting for payment (new -> paid). Later transitions (processing,
        # ready, completed) are driven by staff.
        if self.order.status == Order.Status.NEW:
            from orders.services import transition_order_status

            transition_order_status(
                order=self.order,
                new_status=Order.Status.PAID,
            )
