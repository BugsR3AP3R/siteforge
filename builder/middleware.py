from django.http import Http404
from django.conf import settings


class SiteRouterMiddleware:
    """Route requests from custom domains to the correct site."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        main_domain = getattr(settings, 'MAIN_DOMAIN', 'siteforge.io')

        # Skip platform routes
        if host == main_domain or host.endswith(f'.{main_domain}') or host in ('localhost', '127.0.0.1'):
            # Check for subdomain site routing
            if host.endswith(f'.{main_domain}') and not host.startswith('www.'):
                subdomain = host.replace(f'.{main_domain}', '')
                request.subdomain_site_slug = subdomain
            return self.get_response(request)

        # Custom domain routing
        try:
            from builder.models import Domain
            domain_obj = Domain.objects.select_related('site').filter(
                domain=host, is_verified=True
            ).first()
            if domain_obj:
                request.custom_domain_site = domain_obj.site
        except Exception:
            pass

        return self.get_response(request)
