
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.events.models import Event
from .models import Exhibitor
from django.contrib.auth import authenticate, login

def unified_login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # STAFF USER
            if user.is_staff:
                return redirect('staff_dashboard')

            # EXHIBITOR USER
            event = Event.objects.filter(is_active=True).first()
            if Exhibitor.objects.filter(user=user, event=event).exists():
                return redirect('exhibitor_dashboard')

        return render(request, 'exhibitors/login.html', {
            'error': 'Invalid credentials'
        })

    return render(request, 'exhibitors/login.html')


@login_required
def exhibitor_dashboard(request):

    event = Event.objects.filter(is_active=True).first()
    if not event:
        return redirect('exhibitor_login')

    try:
        exhibitor = Exhibitor.objects.get(
            user=request.user,
            event=event
        )
    except Exhibitor.DoesNotExist:
        return redirect('exhibitor_login')

    total_visits = exhibitor.visits.count()

    return render(request, 'exhibitors/dashboard.html', {
        'exhibitor': exhibitor,
        'total_visits': total_visits
    })

@login_required
def scan_page(request):

    event = Event.objects.filter(is_active=True).first()
    if not event:
        return redirect('exhibitor_login')

    if not Exhibitor.objects.filter(
        user=request.user,
        event=event
    ).exists():
        return redirect('exhibitor_login')

    return render(request, 'exhibitors/scan.html')