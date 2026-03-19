from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('site/<uuid:site_id>/', views.site_detail, name='site_detail'),
    path('site/<uuid:site_id>/delete/', views.delete_site, name='delete_site'),
]
