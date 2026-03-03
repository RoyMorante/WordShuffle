#!/usr/bin/env python
"""
Detailed diagnostic for game-based raffle system.
"""

import os
import sys
import django

sys.path.insert(0, '/d/exhibit')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.events.models import Event
from apps.raffle.models import RaffleEntry, RaffleSetting, RaffleWinner
from apps.viewers.models import Viewer

print("=" * 70)
print("GAME-BASED RAFFLE DIAGNOSTIC")
print("=" * 70)

event = Event.objects.filter(is_active=True).first()
print(f"\n📍 Active Event: {event.name} (ID: {event.id})")

raffle_setting = RaffleSetting.objects.filter(event=event).first()
print(f"📋 Raffle Mode: {raffle_setting.mode}")
print(f"📋 Min Booth Required: {raffle_setting.min_booth_required}")

# Check all RaffleEntry records
print(f"\n{'='*70}")
print("ALL RAFFLE ENTRIES FOR THIS EVENT")
print('='*70)

all_entries = RaffleEntry.objects.filter(event=event)
print(f"Total RaffleEntry records: {all_entries.count()}")

for entry in all_entries:
    print(f"\n  ID: {entry.id}")
    print(f"  Viewer: {entry.viewer.full_name}")
    print(f"  Game Score: {entry.game_score}")
    print(f"  Created: {entry.created_at}")
    
    # Check if winner
    is_winner = RaffleWinner.objects.filter(raffle_entry=entry).exists()
    if is_winner:
        winner_record = RaffleWinner.objects.get(raffle_entry=entry)
        print(f"  ⭐ WINNER - Rank: {winner_record.rank}")

# Test the get_eligible_entries function
print(f"\n{'='*70}")
print("TESTING get_eligible_entries()")
print('='*70)

from apps.raffle.utils import get_eligible_entries

eligible = get_eligible_entries(event)
print(f"\nEligible entries count: {eligible.count()}")

if eligible.exists():
    print("\nEligible entries (should be sorted by game_score DESC):")
    for i, entry in enumerate(eligible, 1):
        print(f"  {i}. {entry.viewer.full_name:30} | Score: {entry.game_score}")
else:
    print("❌ No eligible entries found!")
    
    # Debug: check filtering logic
    print("\n🔍 DEBUGGING FILTERING:")
    print(f"   - Mode: {raffle_setting.mode}")
    print(f"   - Looking for entries with game_score__isnull=False")
    
    entries_with_score = RaffleEntry.objects.filter(
        event=event,
        game_score__isnull=False
    )
    print(f"   - Entries with game_score NOT NULL: {entries_with_score.count()}")
    for e in entries_with_score:
        print(f"     * {e.viewer.full_name}: {e.game_score}")
    
    # Check winners
    winners = RaffleWinner.objects.filter(event=event).values_list('raffle_entry_id', flat=True)
    print(f"   - Already drawn as winners (IDs): {list(winners)}")
    
    # Check what the exclusion looks like
    after_exclude = entries_with_score.exclude(id__in=winners)
    print(f"   - After excluding winners: {after_exclude.count()}")

print(f"\n{'='*70}")
print("✓ DIAGNOSTIC COMPLETE")
print('='*70)
