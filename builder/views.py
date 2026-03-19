from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from django.db import models
import json

from .models import Site, Page, Section, Domain, Media, SITE_TEMPLATES, SITE_TYPES


@login_required
def create_site_step1(request):
    if not request.user.can_create_sites:
        messages.error(request, 'Vous devez avoir un abonnement actif.')
        return redirect('billing:subscribe')
    return render(request, 'builder/create_step1.html', {'site_types': SITE_TYPES})


@login_required
def create_site_step2(request, site_type):
    templates = SITE_TEMPLATES.get(site_type, [])
    if not templates:
        return redirect('builder:create_step1')
    return render(request, 'builder/create_step2.html', {
        'site_type': site_type,
        'templates': templates,
        'site_type_label': dict(SITE_TYPES).get(site_type, site_type),
    })


@login_required
def create_site_step3(request, site_type, template_id):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        custom_domain = request.POST.get('custom_domain', '').strip()
        if not name:
            messages.error(request, 'Le nom du site est requis.')
            return render(request, 'builder/create_step3.html', {
                'site_type': site_type, 'template_id': template_id,
                'site_type_label': dict(SITE_TYPES).get(site_type, site_type),
            })
        templates_list = SITE_TEMPLATES.get(site_type, [])
        template = next((t for t in templates_list if t['id'] == template_id), None)
        colors = template.get('colors', ['#ffffff', '#000000', '#6c63ff']) if template else ['#ffffff', '#000000', '#6c63ff']
        site = Site.objects.create(
            user=request.user, name=name, site_type=site_type, template_id=template_id,
            settings={
                'colors': {'primary': colors[2] if len(colors) > 2 else '#6c63ff', 'bg': colors[0], 'text': '#222222'},
                'fonts': {'heading': 'Syne', 'body': 'DM Sans'},
                'navbar': {'transparent': False, 'sticky': True},
            }
        )
        homepage = Page.objects.create(site=site, title='Accueil', slug='home', is_homepage=True, order=0)
        _create_default_sections(homepage, site_type)
        if custom_domain:
            Domain.objects.create(site=site, domain=custom_domain.lower(), is_primary=True, is_verified=False)
        messages.success(request, f'Site "{name}" créé avec succès !')
        return redirect('builder:editor', site_id=site.id)
    return render(request, 'builder/create_step3.html', {
        'site_type': site_type, 'template_id': template_id,
        'site_type_label': dict(SITE_TYPES).get(site_type, site_type),
    })


def _create_default_sections(page, site_type):
    defaults = {
        'portfolio': [
            ('hero', 0, {'title': 'Bonjour, je suis [Votre Nom]', 'subtitle': 'Designer & Développeur créatif', 'cta_text': 'Voir mon travail', 'cta_url': '#portfolio'}),
            ('portfolio_grid', 1, {'title': 'Mes projets', 'items': []}),
            ('about', 2, {'title': 'À propos', 'text': 'Parlez de vous ici...'}),
            ('contact', 3, {'title': 'Contact', 'email': '', 'show_form': True}),
        ],
        'ecommerce': [
            ('hero', 0, {'title': 'Bienvenue dans notre boutique', 'subtitle': 'Découvrez notre collection', 'cta_text': 'Acheter maintenant'}),
            ('product_grid', 1, {'title': 'Nos produits', 'items': []}),
            ('features', 2, {'title': 'Pourquoi nous choisir', 'items': []}),
            ('newsletter', 3, {'title': 'Restez informé', 'subtitle': 'Inscrivez-vous à notre newsletter'}),
        ],
        'eshop': [
            ('hero', 0, {'title': 'Nouvelle collection', 'subtitle': 'Les dernières tendances', 'cta_text': 'Découvrir'}),
            ('product_grid', 1, {'title': 'Boutique', 'items': []}),
            ('cta', 2, {'title': 'Livraison gratuite dès 50€', 'cta_text': 'En profiter'}),
        ],
        'eart': [
            ('hero', 0, {'title': "Galerie d'art en ligne", 'subtitle': 'Découvrez des œuvres uniques', 'cta_text': 'Explorer'}),
            ('gallery', 1, {'title': 'Œuvres récentes', 'items': []}),
            ('about', 2, {'title': "L'artiste", 'text': 'Présentez votre démarche artistique...'}),
            ('contact', 3, {'title': 'Acquérir une œuvre', 'show_form': True}),
        ],
        'blog': [
            ('hero', 0, {'title': 'Mon Blog', 'subtitle': 'Actualités & Réflexions', 'cta_text': 'Lire les articles'}),
            ('blog_grid', 1, {'title': 'Articles récents', 'items': []}),
            ('newsletter', 2, {'title': 'Newsletter', 'subtitle': 'Recevez les nouveaux articles'}),
        ],
    }
    for sec_type, order, content in defaults.get(site_type, []):
        Section.objects.create(page=page, section_type=sec_type, order=order, content=content)


@login_required
def editor(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    pages = site.pages.all()
    current_page_id = request.GET.get('page')
    if current_page_id:
        current_page = get_object_or_404(Page, id=current_page_id, site=site)
    else:
        current_page = pages.filter(is_homepage=True).first() or pages.first()
    sections = current_page.sections.all() if current_page else []
    templates_list = SITE_TEMPLATES.get(site.site_type, [])
    current_template = next((t for t in templates_list if t['id'] == site.template_id), None)
    return render(request, 'builder/editor.html', {
        'site': site, 'pages': pages, 'current_page': current_page,
        'sections': sections, 'section_types': Section.SECTION_TYPES,
        'current_template': current_template,
        'site_settings_json': json.dumps(site.settings),
    })


@login_required
def api_update_site_settings(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        site.settings = data.get('settings', site.settings)
        site.save()
    return JsonResponse({'status': 'ok'})


@login_required
def api_update_section(request, section_id):
    section = get_object_or_404(Section, id=section_id, page__site__user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'content' in data:
            section.content = data['content']
        if 'settings' in data:
            section.settings = data['settings']
        if 'is_visible' in data:
            section.is_visible = data['is_visible']
        section.save()
    return JsonResponse({'status': 'ok', 'section_id': str(section.id), 'content': section.content})


@login_required
@require_http_methods(['POST'])
def api_reorder_sections(request, page_id):
    page = get_object_or_404(Page, id=page_id, site__user=request.user)
    data = json.loads(request.body)
    for i, section_id in enumerate(data.get('order', [])):
        Section.objects.filter(id=section_id, page=page).update(order=i)
    return JsonResponse({'status': 'ok'})


@login_required
@require_http_methods(['POST'])
def api_add_section(request, page_id):
    page = get_object_or_404(Page, id=page_id, site__user=request.user)
    data = json.loads(request.body)
    section_type = data.get('section_type', 'text')
    max_order = page.sections.aggregate(models.Max('order'))['order__max'] or 0
    section = Section.objects.create(page=page, section_type=section_type, order=max_order + 1, content={})
    return JsonResponse({'status': 'ok', 'section_id': str(section.id)})


@login_required
@require_http_methods(['DELETE'])
def api_delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id, page__site__user=request.user)
    section.delete()
    return JsonResponse({'status': 'ok'})


@login_required
@require_http_methods(['POST'])
def api_publish_site(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    site.status = 'published'
    site.published_at = timezone.now()
    site.save()
    return JsonResponse({'status': 'ok', 'url': site.url})


@login_required
@require_http_methods(['POST'])
def api_add_domain(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    data = json.loads(request.body)
    domain_name = data.get('domain', '').strip().lower()
    if not domain_name:
        return JsonResponse({'error': 'Domaine requis'}, status=400)
    if Domain.objects.filter(domain=domain_name).exists():
        return JsonResponse({'error': 'Ce domaine est déjà utilisé'}, status=400)
    import secrets
    token = secrets.token_hex(16)
    domain = Domain.objects.create(
        site=site, domain=domain_name, verification_token=token,
        is_primary=not site.domains.filter(is_primary=True).exists(),
    )
    return JsonResponse({'status': 'ok', 'domain_id': str(domain.id), 'dns_record': domain.dns_record, 'verification_token': token})


@login_required
def api_verify_domain(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id, site__user=request.user)
    domain.is_verified = True
    domain.verified_at = timezone.now()
    domain.save()
    return JsonResponse({'status': 'verified'})


@login_required
@require_http_methods(['POST'])
def api_upload_media(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Aucun fichier'}, status=400)
    ext = file.name.split('.')[-1].lower()
    file_type = 'image' if ext in ('jpg', 'jpeg', 'png', 'gif', 'webp', 'svg') else 'document'
    media = Media.objects.create(site=site, file=file, file_type=file_type, name=file.name, size=file.size)
    return JsonResponse({'status': 'ok', 'url': media.file.url, 'id': str(media.id)})


def render_site(request, slug):
    site = get_object_or_404(Site, slug=slug, status='published')
    page_slug = request.GET.get('page', 'home')
    page = site.pages.filter(slug=page_slug).first() or site.pages.filter(is_homepage=True).first()
    if not page:
        from django.http import Http404
        raise Http404
    sections = page.sections.filter(is_visible=True)
    template_name = f'sites/{site.template_id}.html'
    from django.template.loader import get_template
    from django.template import TemplateDoesNotExist
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        template_name = 'sites/portfolio_minimal.html'
    return render(request, template_name, {
        'site': site, 'page': page, 'sections': sections,
        'pages': site.pages.filter(is_published=True),
    })


# ─── PREVIEW (sans restriction de statut, login requis) ──────────────────────

@login_required
def preview_site(request, site_id):
    """Prévisualisation dans l'éditeur — pas besoin d'être publié."""
    site = get_object_or_404(Site, id=site_id, user=request.user)
    page_id = request.GET.get('page')
    if page_id:
        page = get_object_or_404(Page, id=page_id, site=site)
    else:
        page = site.pages.filter(is_homepage=True).first() or site.pages.first()

    if not page:
        from django.http import HttpResponse
        return HttpResponse('<html><body style="background:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;color:#aaa"><p>Aucune page — créez une section pour commencer.</p></body></html>')

    sections = page.sections.filter(is_visible=True).order_by('order')

    template_name = f'sites/{site.template_id}.html'
    from django.template.loader import get_template
    from django.template import TemplateDoesNotExist
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        template_name = 'sites/portfolio_minimal.html'

    response = render(request, template_name, {
        'site': site,
        'page': page,
        'sections': sections,
        'pages': site.pages.filter(is_published=True),
        'is_preview': True,
    })
    # Autoriser l'affichage dans une iframe du même domaine
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response
