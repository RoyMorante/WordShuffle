from django.urls import path
from . import views

app_name = 'raffle'

urlpatterns = [
    # Game Selection
    path('games/', views.raffle_game_list, name='game_list'),
    path('games/start/', views.start_game, name='start_game'),
    
    # API
    path('api/games/', views.get_available_games, name='api_games'),
]
