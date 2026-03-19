from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from builder.models import Site, SITE_TYPES
from billing.models import Subscription


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'landing/index.html')


@login_required
def home(request):
    sites = request.user.sites.all()
    subscription = request.user.active_subscription
    return render(request, 'dashboard/home.html', {
        'sites': sites,
        'subscription': subscription,
        'site_count': sites.count(),
        'published_count': sites.filter(status='published').count(),
        'draft_count': sites.filter(status='draft').count(),
    })


@login_required
def site_detail(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    return render(request, 'dashboard/site_detail.html', {
        'site': site,
        'pages': site.pages.all(),
        'domains': site.domains.all(),
        'media_count': site.media_files.count(),
    })


@login_required
def delete_site(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    if request.method == 'POST':
        name = site.name
        site.delete()
        messages.success(request, f'Site "{name}" supprimé.')
        return redirect('dashboard:home')
    return render(request, 'dashboard/delete_site.html', {'site': site})
