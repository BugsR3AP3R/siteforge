from django.contrib import admin
from .models import Subscription, Invoice

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'trial_end', 'created_at']
    list_filter = ['status', 'plan']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'amount', 'status', 'created_at']
