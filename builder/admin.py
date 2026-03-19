from django.contrib import admin
from .models import Site, Page, Section, Domain, Media

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'site_type', 'status', 'created_at']
    list_filter = ['site_type', 'status']
    search_fields = ['name', 'user__email']

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'site', 'is_verified', 'created_at']

admin.site.register(Page)
admin.site.register(Section)
admin.site.register(Media)
