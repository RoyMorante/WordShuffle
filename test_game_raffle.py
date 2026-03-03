#!/usr/bin/env python
"""
Test script to verify game-based raffle implementation.
Run with: python manage.py shell < test_game_raffle.py
"""

import os
import sys
import django

# Add project root to path
sys.path.insert(0, '/d/exhibit')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.events.models import Event
from apps.raffle.models import RaffleEntry, RaffleSetting
from games.models import GameConfig, GameAttempt, GameSession
from apps.viewers.models import Viewer

print("=" * 60)
print("GAME-BASED RAFFLE IMPLEMENTATION TEST")
print("=" * 60)

# Get active event
event = Event.objects.filter(is_active=True).first()
if not event:
    print("❌ No active event found")
    exit(1)

print(f"\n✓ Active Event: {event.name} (ID: {event.id})")

# Check RaffleSetting
raffle_setting = RaffleSetting.objects.filter(event=event).first()
if not raffle_setting:
    print("❌ No RaffleSetting found")
    exit(1)

print(f"✓ Raffle Mode: {raffle_setting.mode}")

# Check if game-based raffle
if raffle_setting.mode != 'game':
    print("\n⚠️  Raffle mode is 'draw', not 'game'")
    print("   To enable game-based raffle, update RaffleSetting.mode to 'game'")
else:
    print("\n✓ Game-based raffle is ENABLED")

# Check GameConfig
game_config = GameConfig.objects.filter(event=event, game_type='word_shuffle', is_active=True).first()
if not game_config:
    print("❌ No active Word Shuffle game config found")
    exit(1)

print(f"✓ Game Config: {game_config.title} (ID: {game_config.id})")

# Check GameSessions
sessions = GameSession.objects.filter(game_config=game_config, event=event)
print(f"✓ Total Game Sessions: {sessions.count()}")

# Get all attempts across sessions
all_attempts = GameAttempt.objects.filter(session__game_config=game_config)
print(f"✓ Total Game Attempts: {all_attempts.count()}")

# Check RaffleEntry game_scores
raffle_entries_with_scores = RaffleEntry.objects.filter(
    event=event,
    game_score__isnull=False
)
print(f"\n✓ RaffleEntries with game_score: {raffle_entries_with_scores.count()}")

if raffle_entries_with_scores.exists():
    print("\n--- Top Players by Game Score ---")
    top_players = raffle_entries_with_scores.order_by('-game_score')[:5]
    for idx, entry in enumerate(top_players, 1):
        print(f"  {idx}. {entry.viewer.full_name:30} | Score: {entry.game_score}")

# Verify get_eligible_entries logic
print("\n" + "=" * 60)
print("TESTING get_eligible_entries() FUNCTION")
print("=" * 60)

from apps.raffle.utils import get_eligible_entries

eligible = get_eligible_entries(event)
print(f"\nEligible entries for {raffle_setting.mode} mode: {eligible.count()}")

if raffle_setting.mode == 'game' and eligible.count() > 0:
    print("\nTop 3 eligible entries (should be ordered by game_score DESC):")
    for idx, entry in enumerate(eligible[:3], 1):
        print(f"  {idx}. {entry.viewer.full_name:30} | Score: {entry.game_score}")
    
    # Verify they're sorted correctly
    scores = list(eligible.values_list('game_score', flat=True)[:3])
    if scores == sorted(scores, reverse=True):
        print("\n✓ Entries are correctly sorted by game_score (highest first)")
    else:
        print(f"\n❌ Entries are NOT correctly sorted! Scores: {scores}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
