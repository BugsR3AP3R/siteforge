from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def active_subscription(self):
        return self.subscriptions.filter(status__in=['active', 'trialing']).first()

    @property
    def is_on_trial(self):
        sub = self.active_subscription
        return sub and sub.status == 'trialing'

    @property
    def trial_days_left(self):
        sub = self.active_subscription
        if sub and sub.status == 'trialing' and sub.trial_end:
            delta = sub.trial_end - timezone.now()
            return max(0, delta.days)
        return 0

    @property
    def can_create_sites(self):
        return self.active_subscription is not None
