from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, LoginForm, ProfileForm
from billing.models import Subscription
from django.conf import settings


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Créer essai gratuit 21 jours
            trial_end = timezone.now() + timezone.timedelta(days=settings.TRIAL_DAYS)
            Subscription.objects.create(
                user=user,
                status='trialing',
                trial_end=trial_end,
                plan='monthly',
            )
            login(request, user)
            messages.success(request, f'Bienvenue ! Votre essai gratuit de {settings.TRIAL_DAYS} jours commence maintenant.')
            return redirect('dashboard:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form, 'trial_days': settings.TRIAL_DAYS})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
