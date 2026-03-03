import json
import random
import time
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.viewers.models import Viewer
from .models import GameSession, GameAttempt, GameContent, GameLevel, GameConfig
from apps.raffle.models import RaffleEntry


# ==========================================
# WORD SHUFFLE UTILITIES
# ==========================================

def shuffle_word(word):
    """Shuffle a word's letters and return the shuffled version."""
    letters = list(word.upper())
    random.shuffle(letters)
    return ''.join(letters)


def calculate_score(is_correct, time_spent, time_limit):
    """
    Calculate score based on correctness and speed.
    
    Scoring:
    - Correct answer: +10 points
    - Wrong answer: 0 points
    - Fast bonus: +2 points (if answered in <= 50% of time limit)
    """
    if not is_correct:
        return 0
    
    base_score = 10
    fast_bonus = 0
    
    # Fast bonus if answered in 50% or less of available time
    if time_spent <= (time_limit * 0.5):
        fast_bonus = 2
    
    return base_score + fast_bonus


# ==========================================
# WORD SHUFFLE VIEWS
# ==========================================

@api_view(['GET'])
def word_shuffle_game_page(request):
    """Render the Word Shuffle game page."""
    return render(request, 'games/word_shuffle.html')


@api_view(['GET'])
def start_word_shuffle_session(request):
    """
    Start a Word Shuffle game session.
    Returns a game session object with initial word to guess.
    
    Query params:
    - game_config_id: ID of the game configuration
    - level_id: ID of the game level
    - viewer_id: ID of the viewer playing
    """
    try:
        game_config_id = request.query_params.get('game_config_id')
        level_id = request.query_params.get('level_id')
        viewer_id = request.query_params.get('viewer_id')
        
        if not all([game_config_id, level_id, viewer_id]):
            return Response(
                {'error': 'Missing required parameters: game_config_id, level_id, viewer_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        game_config = get_object_or_404(GameConfig, id=game_config_id)
        level = get_object_or_404(GameLevel, id=level_id, game_config=game_config)
        viewer = get_object_or_404(Viewer, id=viewer_id)
        
        # Get all active word content for this level
        words = GameContent.objects.filter(
            game_config=game_config,
            level=level,
            content_type='word',
            is_active=True
        )
        
        if not words.exists():
            return Response(
                {'error': 'No words available for this level'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Select a random word
        selected_word_content = random.choice(words)
        word = selected_word_content.data.get('word', '').upper()
        shuffled = shuffle_word(word)
        
        # Store session data in memory/cache for this viewer
        session_data = {
            'game_config_id': game_config_id,
            'level_id': level_id,
            'viewer_id': viewer_id,
            'correct_word': word,
            'word_content_id': selected_word_content.id,
            'points': selected_word_content.points,
            'start_time': time.time(),
        }
        
        return Response({
            'success': True,
            'game_session': {
                'shuffled_word': shuffled,
                'time_limit': level.time_limit_seconds,
                'level_name': level.name,
                'game_title': game_config.title,
            },
            'session_data': session_data,
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def submit_word_shuffle_answer(request):
    """
    Submit an answer for Word Shuffle game.
    
    Expected POST data:
    {
        "user_answer": "INNOVATION",
        "correct_word": "INNOVATION",
        "time_spent": 35,
        "time_limit": 60,
        "game_config_id": 1,
        "level_id": 1,
        "viewer_id": 1,
        "word_content_id": 1
    }
    """
    try:
        user_answer = request.data.get('user_answer', '').strip().upper()
        correct_word = request.data.get('correct_word', '').strip().upper()
        time_spent = int(request.data.get('time_spent', 0))
        time_limit = int(request.data.get('time_limit', 60))
        game_config_id = request.data.get('game_config_id')
        level_id = request.data.get('level_id')
        viewer_id = request.data.get('viewer_id')
        
        if not all([user_answer, correct_word, game_config_id, level_id, viewer_id]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if answer is correct
        is_correct = user_answer == correct_word
        
        # Calculate score
        score = calculate_score(is_correct, time_spent, time_limit)
        
        # Prepare game result data
        game_result = {
            'word': correct_word,
            'user_answer': user_answer,
            'correct': is_correct,
            'time_spent': time_spent,
            'time_limit': time_limit,
            'score': score,
        }
        
        # Try to get or create a game session
        game_config = get_object_or_404(GameConfig, id=game_config_id)
        level = get_object_or_404(GameLevel, id=level_id)
        viewer = get_object_or_404(Viewer, id=viewer_id)
        
        # Get the event from game_config
        event = game_config.event
        
        # Get or create active game session
        session, created = GameSession.objects.get_or_create(
            event=event,
            game_config=game_config,
            level=level,
            is_active=True,
            defaults={'started_by': None}
        )
        
        # Create or update game attempt
        attempt, created = GameAttempt.objects.get_or_create(
            session=session,
            viewer=viewer,
            defaults={
                'score': score,
                'time_spent_seconds': time_spent,
                'raw_answers': [game_result],
                'fastest_correct_time': time_spent if is_correct else None,
            }
        )
        
        # If attempt already exists, append to raw_answers
        if not created:
            raw_answers = attempt.raw_answers or []
            if not isinstance(raw_answers, list):
                raw_answers = [raw_answers]
            raw_answers.append(game_result)
            attempt.raw_answers = raw_answers
            attempt.score += score
            attempt.time_spent_seconds += time_spent
            
            # Update fastest_correct_time for tie-breaking
            if is_correct:
                if attempt.fastest_correct_time is None or time_spent < attempt.fastest_correct_time:
                    attempt.fastest_correct_time = time_spent
            
            attempt.save()
        
        # Update RaffleEntry with game_score for game-based raffle
        raffle_entry, entry_created = RaffleEntry.objects.get_or_create(
            event=event,
            viewer=viewer,
            defaults={'game_score': attempt.score}
        )
        if not entry_created:
            raffle_entry.game_score = attempt.score
            raffle_entry.save()
        
        return Response({
            'success': True,
            'result': {
                'is_correct': is_correct,
                'score': score,
                'correct_word': correct_word,
                'user_answer': user_answer,
                'message': 'Correct! Well done!' if is_correct else f'Wrong! The correct word was: {correct_word}',
            },
            'attempt': {
                'total_score': attempt.score,
                'attempts_count': len(attempt.raw_answers) if attempt.raw_answers else 1,
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_word_shuffle_leaderboard(request):
    """
    Get leaderboard for a Word Shuffle game session.
    
    Query params:
    - game_config_id: ID of the game configuration
    - level_id: ID of the game level
    """
    try:
        game_config_id = request.query_params.get('game_config_id')
        level_id = request.query_params.get('level_id')
        
        if not all([game_config_id, level_id]):
            return Response(
                {'error': 'Missing required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        game_config = get_object_or_404(GameConfig, id=game_config_id)
        level = get_object_or_404(GameLevel, id=level_id)
        event = game_config.event
        
        # Get active session
        session = GameSession.objects.filter(
            event=event,
            game_config=game_config,
            level=level,
            is_active=True
        ).first()
        
        if not session:
            return Response(
                {'error': 'No active game session'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all attempts sorted by score
        attempts = GameAttempt.objects.filter(session=session).order_by('-score')
        
        leaderboard = []
        for attempt in attempts:
            leaderboard.append({
                'rank': len(leaderboard) + 1,
                'viewer_name': attempt.viewer.name,
                'score': attempt.score,
                'time_spent': attempt.time_spent_seconds,
                'attempts_count': len(attempt.raw_answers) if attempt.raw_answers else 0,
            })
        
        return Response({
            'success': True,
            'game_title': game_config.title,
            'level_name': level.name,
            'leaderboard': leaderboard,
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

