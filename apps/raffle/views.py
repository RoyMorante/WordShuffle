from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.events.models import Event
from apps.viewers.models import Viewer
from games.models import GameConfig, GameLevel
from .models import RaffleSetting, RaffleEntry


# ==========================================
# GAME SELECTION VIEWS
# ==========================================

def raffle_game_list(request):
    """
    Display all available games for raffle.
    
    Context variables available:
    - games: List of available GameConfig objects
    - viewer: Current viewer
    - event: Current event
    """
    try:
        # Get viewer from session or request
        viewer_id = request.GET.get('viewer_id') or request.session.get('viewer_id')
        event_id = request.GET.get('event_id') or request.session.get('event_id')
        
        if not viewer_id or not event_id:
            return render(request, 'raffle/error.html', {
                'error': 'Missing viewer or event information'
            }, status=400)
        
        viewer = get_object_or_404(Viewer, id=viewer_id)
        event = get_object_or_404(Event, id=event_id)
        
        # Check if raffle is active and in game mode
        raffle_setting = get_object_or_404(RaffleSetting, event=event)
        
        if not raffle_setting.is_active:
            return render(request, 'raffle/error.html', {
                'error': 'Raffle is not currently active'
            }, status=400)
        
        # Get all active game configurations for this event
        games = GameConfig.objects.filter(
            event=event,
            is_active=True
        ).prefetch_related('gamelevel_set')
        
        # Get levels for each game
        games_data = []
        for game in games:
            levels = game.gamelevel_set.all().order_by('difficulty_order')
            games_data.append({
                'game': game,
                'levels': levels,
                'level_count': levels.count(),
            })
        
        # Get or create raffle entry for viewer
        raffle_entry, created = RaffleEntry.objects.get_or_create(
            event=event,
            viewer=viewer,
            defaults={'game_score': 0}
        )
        
        context = {
            'games_data': games_data,
            'viewer': viewer,
            'event': event,
            'raffle_entry': raffle_entry,
            'raffle_mode': raffle_setting.mode,
        }
        
        return render(request, 'raffle/game_list.html', context)
    
    except Exception as e:
        return render(request, 'raffle/error.html', {
            'error': f'Error loading games: {str(e)}'
        }, status=500)


def start_game(request):
    """
    Redirect to a specific game with parameters.
    
    Query params:
    - game_config_id: ID of the game to start
    - level_id: ID of the difficulty level (optional, defaults to Easy)
    - viewer_id: ID of the viewer
    - event_id: ID of the event
    """
    try:
        game_config_id = request.GET.get('game_config_id')
        level_id = request.GET.get('level_id')
        viewer_id = request.GET.get('viewer_id')
        event_id = request.GET.get('event_id')
        
        if not all([game_config_id, viewer_id, event_id]):
            return render(request, 'raffle/error.html', {
                'error': 'Missing required parameters'
            }, status=400)
        
        # Verify game and viewer exist
        game = get_object_or_404(GameConfig, id=game_config_id)
        viewer = get_object_or_404(Viewer, id=viewer_id)
        event = get_object_or_404(Event, id=event_id)
        
        # If no level specified, get the first (easiest) level
        if not level_id:
            level = game.gamelevel_set.order_by('difficulty_order').first()
            if not level:
                return render(request, 'raffle/error.html', {
                    'error': 'No difficulty levels available for this game'
                }, status=400)
            level_id = level.id
        else:
            level = get_object_or_404(GameLevel, id=level_id, game_config=game)
        
        # Build game URL based on game type
        game_url_map = {
            'word_shuffle': '/games/word-shuffle/',
            'memory': '/games/memory/',
            'quiz': '/games/quiz/',
            'reaction': '/games/reaction/',
        }
        
        base_url = game_url_map.get(game.game_type)
        if not base_url:
            return render(request, 'raffle/error.html', {
                'error': f'Unknown game type: {game.game_type}'
            }, status=400)
        
        # Redirect to game with parameters
        game_url = f"{base_url}?game_config_id={game_config_id}&level_id={level_id}&viewer_id={viewer_id}&event_id={event_id}"
        return redirect(game_url)
    
    except Exception as e:
        return render(request, 'raffle/error.html', {
            'error': f'Error starting game: {str(e)}'
        }, status=500)


@api_view(['GET'])
def get_available_games(request):
    """
    API endpoint to get all available games for an event.
    
    Query params:
    - event_id: ID of the event
    """
    try:
        event_id = request.query_params.get('event_id')
        
        if not event_id:
            return Response(
                {'error': 'Missing event_id parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event = get_object_or_404(Event, id=event_id)
        
        # Get all active games
        games = GameConfig.objects.filter(
            event=event,
            is_active=True
        ).prefetch_related('gamelevel_set')
        
        games_list = []
        for game in games:
            levels = game.gamelevel_set.all().order_by('difficulty_order')
            games_list.append({
                'id': game.id,
                'title': game.title,
                'game_type': game.game_type,
                'description': game.title,
                'levels': [
                    {
                        'id': level.id,
                        'name': level.name,
                        'time_limit': level.time_limit_seconds,
                    }
                    for level in levels
                ],
            })
        
        return Response({
            'success': True,
            'event_id': event_id,
            'games': games_list,
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
