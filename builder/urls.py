from django.urls import path
from . import views

app_name = 'builder'

urlpatterns = [
    path('new/', views.create_site_step1, name='create_step1'),
    path('new/<str:site_type>/', views.create_site_step2, name='create_step2'),
    path('new/<str:site_type>/<str:template_id>/', views.create_site_step3, name='create_step3'),
    path('editor/<uuid:site_id>/', views.editor, name='editor'),
    path('preview/<uuid:site_id>/', views.preview_site, name='preview_site'),
    path('site/<slug:slug>/', views.render_site, name='render_site'),

    # API
    path('api/site/<uuid:site_id>/settings/', views.api_update_site_settings, name='api_site_settings'),
    path('api/site/<uuid:site_id>/publish/', views.api_publish_site, name='api_publish'),
    path('api/site/<uuid:site_id>/domain/', views.api_add_domain, name='api_add_domain'),
    path('api/site/<uuid:site_id>/media/', views.api_upload_media, name='api_media'),
    path('api/page/<uuid:page_id>/sections/reorder/', views.api_reorder_sections, name='api_reorder'),
    path('api/page/<uuid:page_id>/sections/add/', views.api_add_section, name='api_add_section'),
    path('api/section/<uuid:section_id>/', views.api_update_section, name='api_section'),
    path('api/section/<uuid:section_id>/delete/', views.api_delete_section, name='api_delete_section'),
    path('api/domain/<uuid:domain_id>/verify/', views.api_verify_domain, name='api_verify_domain'),
]
