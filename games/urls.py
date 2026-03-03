from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    # Word Shuffle Game Page
    path('word-shuffle/', views.word_shuffle_game_page, name='word_shuffle_page'),
    
    # Word Shuffle Game Endpoints
    path('word-shuffle/start/', views.start_word_shuffle_session, name='start_word_shuffle'),
    path('word-shuffle/submit/', views.submit_word_shuffle_answer, name='submit_word_shuffle'),
    path('word-shuffle/leaderboard/', views.get_word_shuffle_leaderboard, name='word_shuffle_leaderboard'),
]
