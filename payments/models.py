from django.db import models
from django.utils import timezone

from orders.models import Order
from payments.encryption import decrypt_value, encrypt_value, mask_key


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


class RestaurantPaymentConfig(models.Model):
    """Per-restaurant payment gateway configuration.

    Owner sets Midtrans server/client keys per resto so funds settle directly
    to their Midtrans account. Falls back to dummy gateway when not configured.
    Keys are stored encrypted at rest.
    """

    class Gateway(models.TextChoices):
        DUMMY = 'dummy', 'Dummy (Simulasi)'
        MIDTRANS = 'midtrans', 'Midtrans'

    restaurant = models.OneToOneField(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='payment_config',
    )
    gateway = models.CharField(
        max_length=20,
        choices=Gateway.choices,
        default=Gateway.DUMMY,
    )
    # Encrypted storage - raw value is Fernet token
    midtrans_server_key_encrypted = models.TextField(blank=True, default='')
    midtrans_client_key_encrypted = models.TextField(blank=True, default='')
    midtrans_is_production = models.BooleanField(default=False)
    is_active = models.BooleanField(
        default=True,
        help_text='Nonaktifkan tanpa menghapus key.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Restaurant payment config'
        verbose_name_plural = 'Restaurant payment configs'

    def __str__(self):
        return f'Payment config - {self.restaurant.name} ({self.gateway})'

    # -- encrypted accessors --

    @property
    def midtrans_server_key(self) -> str:
        return decrypt_value(self.midtrans_server_key_encrypted)

    @midtrans_server_key.setter
    def midtrans_server_key(self, value: str):
        self.midtrans_server_key_encrypted = encrypt_value(
            value.strip() if value else ''
        )

    @property
    def midtrans_client_key(self) -> str:
        return decrypt_value(self.midtrans_client_key_encrypted)

    @midtrans_client_key.setter
    def midtrans_client_key(self, value: str):
        self.midtrans_client_key_encrypted = encrypt_value(
            value.strip() if value else ''
        )

    @property
    def masked_server_key(self) -> str:
        return mask_key(self.midtrans_server_key)

    @property
    def masked_client_key(self) -> str:
        return mask_key(self.midtrans_client_key)

    @property
    def is_midtrans_configured(self) -> bool:
        return bool(
            self.gateway == self.Gateway.MIDTRANS
            and self.is_active
            and self.midtrans_server_key
            and self.midtrans_client_key
        )

    @property
    def is_configured(self) -> bool:
        if self.gateway == self.Gateway.MIDTRANS:
            return self.is_midtrans_configured
        return self.gateway == self.Gateway.DUMMY
