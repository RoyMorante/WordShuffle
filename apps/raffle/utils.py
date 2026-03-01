from django.db.models import Count
from apps.raffle.models import RaffleSetting, RaffleEntry
from apps.raffle.models import RaffleWinner


def get_eligible_entries(event):

    raffle_setting = RaffleSetting.objects.get(event=event)
    min_required = raffle_setting.min_booth_required

    # Exclude already drawn winners
    winners = RaffleWinner.objects.filter(event=event) \
        .values_list('raffle_entry_id', flat=True)

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