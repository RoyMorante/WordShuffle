from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from apps.exhibitors.views import unified_login, exhibitor_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.viewers.urls')),
    
    # path('exhibitors/login/', 
    #      auth_views.LoginView.as_view(
    #          template_name='exhibitors/login.html',
    #          redirect_authenticated_user=True
    #      ),
    #      name='exhibitor_login'),
    path('exhibitors/login/', unified_login, name='exhibitor_login'),

    path('exhibitors/logout/', exhibitor_logout, name='exhibitor_logout'),
    
    path('exhibitors/', include('apps.exhibitors.urls')),
    path('adminpanel/', include('apps.core.urls')),
    path('visits/', include('apps.visits.urls')),
    path('voting/', include('apps.voting.urls')),
    path('raffle/', include('apps.raffle.urls')),
    path('games/', include('games.urls')),
]

