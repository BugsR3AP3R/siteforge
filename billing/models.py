from django.db import models
from django.utils import timezone
import uuid


class Plan(models.Model):
    INTERVAL_CHOICES = [('monthly', 'Mensuel'), ('yearly', 'Annuel')]
    name = models.CharField(max_length=100)
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stripe_price_id = models.CharField(max_length=200, blank=True)
    max_sites = models.IntegerField(default=-1)  # -1 = illimité
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.interval})"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('trialing', 'Essai gratuit'),
        ('active', 'Actif'),
        ('past_due', 'Paiement en retard'),
        ('canceled', 'Annulé'),
        ('unpaid', 'Impayé'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=[('monthly', 'Mensuel'), ('yearly', 'Annuel')], default='monthly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    stripe_subscription_id = models.CharField(max_length=200, blank=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} — {self.status}"

    @property
    def is_active(self):
        return self.status in ['active', 'trialing']

    @property
    def trial_days_remaining(self):
        if self.status == 'trialing' and self.trial_end:
            delta = self.trial_end - timezone.now()
            return max(0, delta.days)
        return 0

    @property
    def monthly_price(self):
        return 9.99 if self.plan == 'monthly' else 7.99

    def cancel(self):
        self.status = 'canceled'
        self.canceled_at = timezone.now()
        self.save()


class Invoice(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    stripe_invoice_id = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, default='draft')
    invoice_pdf = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Facture {self.stripe_invoice_id} — {self.amount}€"
