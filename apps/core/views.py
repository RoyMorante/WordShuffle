from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from apps.events.models import Event
from apps.viewers.models import Viewer
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from apps.voting.models import Vote, VoteScore, Criteria
from apps.raffle.models import RaffleSetting, RaffleEntry
from apps.visits.models import Visit
from apps.exhibitors.models import Exhibitor
from apps.viewers.models import Viewer
from django.db.models import Count, Sum, F
from apps.voting.models import VoteScore
from apps.raffle.models import RaffleSetting
from apps.visits.models import Visit

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.events.models import Event
from apps.viewers.models import Viewer

from apps.raffle.models import RaffleSetting
import random
from django.http import JsonResponse
from apps.raffle.utils import get_eligible_entries
from apps.raffle.models import RaffleWinner

@login_required
def staff_dashboard(request):

    if not request.user.is_staff:
        return redirect('exhibitor_login')

    return render(request, 'staff/dashboard.html')

@login_required
def staff_generate_qr(request):

    if not request.user.is_staff:
        return redirect('exhibitor_login')

    event = Event.objects.filter(is_active=True).first()
    if not event:
        return render(request, 'staff/generate_qr.html', {
            'error': 'No active event'
        })

    if request.method == 'POST':

        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')
        user_type = request.POST.get('user_type')
        department = request.POST.get('department')

        viewer = Viewer.objects.create(
            event=event,
            email=email,
            full_name=full_name,
            gender=gender,
            user_type=user_type,
            department=department,
            device_identifier="STAFF_GENERATED"
        )

        return render(request, 'staff/print_qr.html', {
            'viewer': viewer
        })

    return render(request, 'staff/generate_qr.html')


@login_required
def staff_vote_page(request):

    if not request.user.is_staff:
        return redirect('exhibitor_login')

    event = Event.objects.filter(is_active=True).first()
    if not event:
        return render(request, 'staff/vote_station.html', {
            'error': 'No active event'
        })

    exhibitors = Exhibitor.objects.filter(event=event, is_active=True)
    criteria_list = Criteria.objects.filter(event=event, is_active=True)

    return render(request, 'staff/vote_station.html', {
        'exhibitors': exhibitors,
        'criteria_list': criteria_list
    })
    

@login_required
@require_POST
def validate_viewer_for_vote(request):

    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    qr_token = request.POST.get('qr_token')

    event = Event.objects.filter(is_active=True).first()
    if not event:
        return JsonResponse({'error': 'No active event'}, status=400)

    viewer = Viewer.objects.filter(
        qr_token=qr_token,
        event=event
    ).first()

    if not viewer:
        return JsonResponse({'error': 'Invalid QR'}, status=404)

    # Already voted?
    if Vote.objects.filter(viewer=viewer).exists():
        return JsonResponse({'error': 'Already voted'}, status=400)

    # Visit threshold
    visit_count = Visit.objects.filter(
        viewer=viewer,
        event=event
    ).count()

    raffle_setting = RaffleSetting.objects.filter(event=event).first()
    min_required = raffle_setting.min_booth_required if raffle_setting else 1

    if visit_count < min_required:
        return JsonResponse({
            'error': f'Minimum {min_required} booth visits required'
        }, status=400)

    return JsonResponse({
        'status': 'valid',
        'viewer_id': viewer.id,
        'viewer_name': viewer.full_name
    })
    

@login_required
@require_POST
def staff_submit_vote(request):

    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    viewer_id = request.POST.get('viewer_id')

    event = Event.objects.filter(is_active=True).first()
    viewer = Viewer.objects.get(id=viewer_id)

    exhibitors = Exhibitor.objects.filter(event=event, is_active=True)
    criteria_list = Criteria.objects.filter(event=event, is_active=True)

    with transaction.atomic():

        vote = Vote.objects.create(
            event=event,
            viewer=viewer
        )

        for exhibitor in exhibitors:
            for criteria in criteria_list:
                score = request.POST.get(
                    f"score_{exhibitor.id}_{criteria.id}"
                )
                if score:
                    VoteScore.objects.create(
                        vote=vote,
                        exhibitor=exhibitor,
                        criteria=criteria,
                        score=int(score)
                    )

        RaffleEntry.objects.get_or_create(
            event=event,
            viewer=viewer
        )

    return JsonResponse({'status': 'success'})



@login_required
def live_dashboard(request):

    event = Event.objects.filter(is_active=True).first()
    if not event:
        return render(request, 'staff/live_dashboard.html', {
            'error': 'No active event'
        })

    # Totals
    total_viewers = Viewer.objects.filter(event=event).count()
    total_visits = Visit.objects.filter(event=event).count()
    total_votes = Vote.objects.filter(event=event).count()

    # Visit ranking
    visit_ranking = Visit.objects.filter(event=event) \
        .values('exhibitor__name') \
        .annotate(total=Count('id')) \
        .order_by('-total')

    # Weighted score ranking
    score_ranking = VoteScore.objects.filter(vote__event=event) \
        .values('exhibitor__name') \
        .annotate(total_score=Sum(
            F('score') * F('criteria__weight')
        )) \
        .order_by('-total_score')

    raffle_setting = RaffleSetting.objects.filter(event=event).first()

    return render(request, 'staff/live_dashboard.html', {
        'total_viewers': total_viewers,
        'total_visits': total_visits,
        'total_votes': total_votes,
        'visit_ranking': visit_ranking,
        'score_ranking': score_ranking,
        'raffle_setting': raffle_setting
    })
    




@login_required
def staff_retrieve_qr(request):

    if not request.user.is_staff:
        return redirect('exhibitor_login')

    event = Event.objects.filter(is_active=True).first()

    if not event:
        return render(request, 'staff/retrieve_qr.html', {
            'error': 'No active event'
        })

    if request.method == 'POST':

        email = request.POST.get('email')

        viewer = Viewer.objects.filter(
            event=event,
            email=email
        ).first()

        if viewer:
            return render(request, 'staff/print_qr.html', {
                'viewer': viewer
            })

        return render(request, 'staff/retrieve_qr.html', {
            'error': 'Visitor not found'
        })

    return render(request, 'staff/retrieve_qr.html')






@login_required
def staff_raffle_control(request):

    if not request.user.is_staff:
        return redirect('exhibitor_login')

    event = Event.objects.filter(is_active=True).first()

    if not event:
        return render(request, 'staff/raffle_control.html', {
            'error': 'No active event'
        })

    raffle_setting, created = RaffleSetting.objects.get_or_create(
        event=event
    )

    if request.method == 'POST':

        raffle_setting.mode = request.POST.get('mode')
        raffle_setting.min_booth_required = int(
            request.POST.get('min_booth_required')
        )
        raffle_setting.game_threshold = int(
            request.POST.get('game_threshold')
        )
        raffle_setting.is_active = True if request.POST.get('is_active') else False

        raffle_setting.save()

        return render(request, 'staff/raffle_control.html', {
            'raffle_setting': raffle_setting,
            'success': 'Settings updated successfully'
        })

    return render(request, 'staff/raffle_control.html', {
        'raffle_setting': raffle_setting
    })
    
    
@login_required
def raffle_draw_page(request):

    if not request.user.is_staff:
        return redirect('exhibitor_login')

    event = Event.objects.filter(is_active=True).first()

    winners = []
    if event:
        winners = RaffleWinner.objects.filter(
            event=event
        ).select_related(
            'raffle_entry__viewer'
        ).order_by('rank')

    return render(request, 'staff/raffle_draw.html', {
        'winners': winners
    })

@login_required
def raffle_spin(request):

    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    event = Event.objects.filter(is_active=True).first()

    eligible_entries = list(get_eligible_entries(event))

    if not eligible_entries:
        return JsonResponse({'error': 'No more eligible entries'})

    winner_entry = random.choice(eligible_entries)

    # Determine next rank
    current_count = RaffleWinner.objects.filter(event=event).count()
    next_rank = current_count + 1

    RaffleWinner.objects.create(
        event=event,
        raffle_entry=winner_entry,
        rank=next_rank
    )

    return JsonResponse({
        'winner_name': winner_entry.viewer.full_name,
        'rank': next_rank
    })
    

