from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from .models import Subscription, Invoice
import json


@login_required
def billing_home(request):
    subscription = request.user.active_subscription
    invoices = []
    if subscription:
        invoices = subscription.invoices.all()[:10]
    return render(request, 'billing/home.html', {
        'subscription': subscription,
        'invoices': invoices,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def subscribe(request):
    if request.method == 'POST':
        plan = request.POST.get('plan', 'monthly')
        # En production: créer une session Stripe Checkout
        # Pour la démo, on active directement l'abonnement
        sub = request.user.active_subscription
        if sub:
            sub.status = 'active'
            sub.plan = plan
            sub.save()
            messages.success(request, f'Abonnement {plan} activé avec succès !')
        return redirect('billing:home')
    return render(request, 'billing/subscribe.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def cancel_subscription(request):
    if request.method == 'POST':
        sub = request.user.active_subscription
        if sub:
            sub.cancel()
            messages.warning(request, 'Votre abonnement a été annulé. Vous gardez accès jusqu\'à la fin de la période.')
        return redirect('billing:home')
    return render(request, 'billing/cancel.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    # Traitement du webhook Stripe en production
    return HttpResponse(status=200)
