from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import transaction
from apps.events.models import Event
from apps.viewers.models import Viewer
from apps.exhibitors.models import Exhibitor
from apps.visits.models import Visit
from apps.raffle.models import RaffleSetting, RaffleEntry
from .models import Criteria, Vote, VoteScore


def vote_page(request):

    viewer_id = request.session.get('viewer_id')
    if not viewer_id:
        return redirect('viewer_register')

    try:
        viewer = Viewer.objects.get(id=viewer_id)
    except Viewer.DoesNotExist:
        return redirect('viewer_register')

    event = Event.objects.filter(is_active=True).first()
    if not event:
        return HttpResponse("No active event")

    # Prevent duplicate vote
    if Vote.objects.filter(viewer=viewer).exists():
        # return HttpResponse("You have already voted.")
        # make above as alert and redirect to dashboard
        return redirect('viewer_dashboard')

    # Visit threshold check
    visit_count = Visit.objects.filter(
        viewer=viewer,
        event=event
    ).count()

    raffle_setting = RaffleSetting.objects.filter(event=event).first()
    min_required = raffle_setting.min_booth_required if raffle_setting else 1

    if visit_count < min_required:
        return HttpResponse(
            f"You must visit at least {min_required} booths before voting."
        )
        # make above as alert and redirect to dashboard
        # return redirect('viewer_dashboard')

    exhibitors = Exhibitor.objects.filter(event=event, is_active=True)
    criteria_list = Criteria.objects.filter(event=event, is_active=True)

    if request.method == 'POST':

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

            # Auto create raffle entry
            RaffleEntry.objects.get_or_create(
                event=event,
                viewer=viewer
            )

        
        # return HttpResponse("Vote submitted successfully.")
        # make above as alert and redirect to dashboard
        return redirect('viewer_dashboard')

    return render(request, 'voting/vote.html', {
        'exhibitors': exhibitors,
        'criteria_list': criteria_list
    })