from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.viewer_register, name='viewer_register'),
    path('', views.viewer_dashboard, name='viewer_dashboard'),
]