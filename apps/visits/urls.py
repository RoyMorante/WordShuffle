from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_viewer, name='scan_viewer'),
]