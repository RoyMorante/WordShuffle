from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.viewer_register, name='viewer_register'),
    path('', views.viewer_dashboard, name='viewer_dashboard'),
    path('viewer/auto-login/', views.auto_login, name='viewer_auto_login'),
    path('viewers/login/', views.viewer_login, name='viewer_login'),
    path('logout/', views.viewer_logout, name='viewer_logout'),
]