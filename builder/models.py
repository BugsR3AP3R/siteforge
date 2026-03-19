from django.db import models
from django.utils.text import slugify
import uuid
import json


SITE_TYPES = [
    ('portfolio', 'Portfolio'),
    ('ecommerce', 'E-Commerce'),
    ('eshop', 'E-Shop'),
    ('eart', 'E-Art / Galerie'),
    ('blog', 'Blog / News'),
]

SITE_TEMPLATES = {
    'portfolio': [
        {'id': 'portfolio_minimal', 'name': 'Minimal Dark', 'preview': 'preview_portfolio_minimal.jpg',
         'colors': ['#0a0a0a', '#ffffff', '#6c63ff'], 'style': 'minimal'},
        {'id': 'portfolio_bold', 'name': 'Bold Creative', 'preview': 'preview_portfolio_bold.jpg',
         'colors': ['#1a1a2e', '#e94560', '#ffffff'], 'style': 'bold'},
        {'id': 'portfolio_clean', 'name': 'Clean Light', 'preview': 'preview_portfolio_clean.jpg',
         'colors': ['#f8f8f8', '#222222', '#0066ff'], 'style': 'clean'},
    ],
    'ecommerce': [
        {'id': 'ecommerce_modern', 'name': 'Modern Store', 'preview': 'preview_ecommerce_modern.jpg',
         'colors': ['#ffffff', '#111111', '#ff6b35'], 'style': 'modern'},
        {'id': 'ecommerce_luxury', 'name': 'Luxury Brand', 'preview': 'preview_ecommerce_luxury.jpg',
         'colors': ['#1a1a1a', '#d4af37', '#ffffff'], 'style': 'luxury'},
        {'id': 'ecommerce_fresh', 'name': 'Fresh & Clean', 'preview': 'preview_ecommerce_fresh.jpg',
         'colors': ['#f0f7f4', '#2d6a4f', '#ffffff'], 'style': 'fresh'},
    ],
    'eshop': [
        {'id': 'eshop_vibrant', 'name': 'Vibrant', 'preview': 'preview_eshop_vibrant.jpg',
         'colors': ['#ff4081', '#3f51b5', '#ffffff'], 'style': 'vibrant'},
        {'id': 'eshop_minimal', 'name': 'Minimal Shop', 'preview': 'preview_eshop_minimal.jpg',
         'colors': ['#fafafa', '#333333', '#e91e63'], 'style': 'minimal'},
        {'id': 'eshop_dark', 'name': 'Dark Market', 'preview': 'preview_eshop_dark.jpg',
         'colors': ['#121212', '#bb86fc', '#03dac6'], 'style': 'dark'},
    ],
    'eart': [
        {'id': 'eart_gallery', 'name': 'Gallery Noir', 'preview': 'preview_eart_gallery.jpg',
         'colors': ['#000000', '#ffffff', '#c9a84c'], 'style': 'gallery'},
        {'id': 'eart_colorful', 'name': 'Colorful Canvas', 'preview': 'preview_eart_colorful.jpg',
         'colors': ['#ffecd2', '#fcb69f', '#a18cd1'], 'style': 'colorful'},
        {'id': 'eart_editorial', 'name': 'Editorial Art', 'preview': 'preview_eart_editorial.jpg',
         'colors': ['#fdf6ec', '#2c2c2c', '#d4380d'], 'style': 'editorial'},
    ],
    'blog': [
        {'id': 'blog_magazine', 'name': 'Magazine Pro', 'preview': 'preview_blog_magazine.jpg',
         'colors': ['#ffffff', '#1a1a1a', '#d63031'], 'style': 'magazine'},
        {'id': 'blog_writer', 'name': 'The Writer', 'preview': 'preview_blog_writer.jpg',
         'colors': ['#f9f6f0', '#2c2c2c', '#6c5ce7'], 'style': 'writer'},
        {'id': 'blog_tech', 'name': 'Tech Blog', 'preview': 'preview_blog_tech.jpg',
         'colors': ['#0d1117', '#58a6ff', '#ffffff'], 'style': 'tech'},
    ],
}


class Site(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('suspended', 'Suspendu'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    site_type = models.CharField(max_length=20, choices=SITE_TYPES)
    template_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    # Personnalisation globale
    settings = models.JSONField(default=dict)
    # Exemple: {
    #   "colors": {"primary": "#6c63ff", "secondary": "#ff6584", "bg": "#ffffff", "text": "#222"},
    #   "fonts": {"heading": "Syne", "body": "DM Sans"},
    #   "navbar": {"transparent": true, "sticky": true},
    # }

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Site.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def primary_domain(self):
        return self.domains.filter(is_primary=True).first()

    @property
    def url(self):
        domain = self.primary_domain
        if domain and domain.is_verified:
            return f"https://{domain.domain}"
        return f"https://{self.slug}.siteforge.io"

    def get_settings(self, key, default=None):
        return self.settings.get(key, default)


class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    is_homepage = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ['site', 'slug']

    def __str__(self):
        return f"{self.site.name} / {self.title}"


class Section(models.Model):
    SECTION_TYPES = [
        ('hero', 'Hero Banner'),
        ('about', 'À propos'),
        ('services', 'Services'),
        ('portfolio_grid', 'Grille Portfolio'),
        ('testimonials', 'Témoignages'),
        ('contact', 'Contact'),
        ('product_grid', 'Grille Produits'),
        ('features', 'Fonctionnalités'),
        ('team', 'Équipe'),
        ('gallery', 'Galerie'),
        ('blog_grid', 'Grille Blog'),
        ('newsletter', 'Newsletter'),
        ('stats', 'Statistiques'),
        ('pricing', 'Tarifs'),
        ('faq', 'FAQ'),
        ('cta', 'Call to Action'),
        ('text', 'Texte libre'),
        ('video', 'Vidéo'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    content = models.JSONField(default=dict)
    # Exemple hero: {"title": "Mon titre", "subtitle": "...", "bg_image": "...", "cta_text": "Voir mon travail"}
    # Exemple product_grid: {"products": [{"name": "...", "price": 29.99, "image": "..."}]}
    settings = models.JSONField(default=dict)
    # Exemple: {"bg_color": "#fff", "padding": "large", "text_align": "center"}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.page} / {self.section_type}"


class Domain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='domains')
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    dns_instructions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.domain

    def generate_verification_token(self):
        import secrets
        self.verification_token = secrets.token_hex(16)
        self.save()

    @property
    def dns_record(self):
        return {
            'type': 'CNAME',
            'name': self.domain,
            'value': 'sites.siteforge.io',
            'ttl': 3600,
        }


class Media(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='media_files')
    file = models.FileField(upload_to='sites/media/')
    file_type = models.CharField(max_length=20)  # image, video, document
    name = models.CharField(max_length=200)
    size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
