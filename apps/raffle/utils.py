from django.db.models import Count, OuterRef, Subquery
from apps.raffle.models import RaffleSetting, RaffleEntry
from apps.raffle.models import RaffleWinner


def get_eligible_entries(event):

    raffle_setting = RaffleSetting.objects.get(event=event)
    min_required = raffle_setting.min_booth_required

    # Exclude already drawn winners
    winners = RaffleWinner.objects.filter(event=event) \
        .values_list('raffle_entry_id', flat=True)

    # For game-based raffle, filter by game_score instead of votes/visits
    if raffle_setting.mode == 'game':
        from games.models import GameAttempt
        
        # Get fastest correct time for each player (for tie-breaking)
        fastest_time = GameAttempt.objects.filter(
            viewer=OuterRef('viewer'),
            fastest_correct_time__isnull=False
        ).order_by('fastest_correct_time').values('fastest_correct_time')[:1]
        
        # Sort by game_score DESC (highest first), then by fastest_correct_time ASC (fastest first) for tie-breaking
        eligible_entries = RaffleEntry.objects.filter(
            event=event,
            game_score__isnull=False
        ).exclude(
            id__in=winners
        ).annotate(
            fastest_time=Subquery(fastest_time)
        ).order_by('-game_score', 'fastest_time')
    else:
        # For draw-based raffle, require votes and minimum booth visits
        eligible_entries = RaffleEntry.objects.filter(
            event=event,
            viewer__vote__isnull=False
        ).exclude(
            id__in=winners
        ).annotate(
            visit_count=Count('viewer__visits')
        ).filter(
            visit_count__gte=min_required
        )

    return eligible_entries


# def get_eligible_entries(event):

#     raffle_setting = RaffleSetting.objects.get(event=event)
#     min_required = raffle_setting.min_booth_required

#     eligible_entries = RaffleEntry.objects.filter(
#         event=event,
#         viewer__vote__isnull=False
#     ).annotate(
#         visit_count=Count('viewer__visits')
#     ).filter(
#         visit_count__gte=min_required
#     )

#     return eligible_entries


# Example Implementation

# AUTO RAFFLE DRAW (Random)
# import random
# from raffle.utils import get_eligible_entries
# def draw_winner(event):
#     eligible_entries = list(get_eligible_entries(event))
#     if not eligible_entries:
#         return None
#     winner = random.choice(eligible_entries)
#     return winner

# GAME MODE WINNER
# def get_game_winner(event):
#     eligible_entries = get_eligible_entries(event)
#     winner = eligible_entries.order_by('-game_score').first()
#     return winner