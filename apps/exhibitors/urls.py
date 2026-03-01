

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.exhibitor_dashboard, name='exhibitor_dashboard'),
    path('scan/', views.scan_page, name='exhibitor_scan'),
]