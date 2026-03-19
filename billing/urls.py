from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.billing_home, name='home'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('cancel/', views.cancel_subscription, name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]
