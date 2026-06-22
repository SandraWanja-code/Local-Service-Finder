from django.db import models
from django.contrib.auth.models import User


class PaymentRecord(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("mpesa", "M-Pesa"),
    ]

    # String reference prevents circular import
    service_request = models.ForeignKey(
        "requests.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="payment_records"
    )

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_made"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    mpesa_code = models.CharField(
        max_length=30,
        blank=True
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.service_request} - {self.amount_paid}"


class TransactionLog(models.Model):
    payment_record = models.ForeignKey(
        PaymentRecord,
        on_delete=models.CASCADE,
        related_name="transaction_logs"
    )

    action = models.CharField(
        max_length=100
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_actions"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.action} - {self.payment_record}"