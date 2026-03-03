from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from apps.events.models import Event
from .models import Viewer
from apps.raffle.models import RaffleSetting

@require_POST
def auto_login(request):

    event = Event.objects.filter(is_active=True).first()
    
    device_id = request.POST.get('device_id')

    if not event or not device_id:
        return JsonResponse({'status': 'not_found'})

    viewer = Viewer.objects.filter(
        event=event,
        device_identifier=device_id
    ).first()

    if viewer:
        request.session.flush()
        request.session['viewer_id'] = viewer.id
        return JsonResponse({'status': 'found'})

    return JsonResponse({'status': 'not_found'})


def viewer_logout(request):
    """Logout the current viewer and clear session."""
    # Set a flag to prevent auto-login on next page load
    response = redirect('viewer_register')
    response.set_cookie('just_logged_out', 'true', max_age=60)  # 60 seconds
    request.session.flush()
    return response


def viewer_dashboard(request):

    event = Event.objects.filter(is_active=True).first()
    viewer_id = request.session.get('viewer_id')

    if not event or not viewer_id:
        return redirect('viewer_register')

    try:
        viewer = Viewer.objects.get(id=viewer_id, event=event)
    except Viewer.DoesNotExist:
        request.session.flush()
        return redirect('viewer_register')

    return render(request, 'viewers/dashboard.html', {
        'viewer': viewer,
        'raffle_eligible': viewer.visits.count() >= RaffleSetting.objects.get(event=event).min_booth_required,  # Example eligibility condition
        'raffle_mode': RaffleSetting.objects.get(event=event).mode
    })
    
def viewer_register(request):

    event = Event.objects.filter(is_active=True).first()

    if not event:
        return HttpResponse("No active event")

    if request.method == 'POST':

        email = request.POST.get('email')
        device_id = request.POST.get('device_id')

        existing = Viewer.objects.filter(
            event=event,
            email=email
        ).first()

        if existing:
            return render(request, 'viewers/login.html', {
                'error': 'Email already registered. Please login.'
            })

        viewer = Viewer.objects.create(
            event=event,
            email=email,
            device_identifier=device_id,
            full_name=request.POST.get('full_name'),
            gender=request.POST.get('gender'),
            user_type=request.POST.get('user_type'),
            department=request.POST.get('department'),
        )

        request.session.flush()
        request.session['viewer_id'] = viewer.id

        return redirect('viewer_dashboard')

    return render(request, 'viewers/register.html')



def viewer_login(request):

    event = Event.objects.filter(is_active=True).first()

    if not event:
        return render(request, 'viewers/login.html', {
            'error': 'No active event'
        })

    if request.method == 'POST':

        email = request.POST.get('email')
        device_id = request.POST.get('device_id')

        viewer = Viewer.objects.filter(
            event=event,
            email=email
        ).first()

        if not viewer:
            return render(request, 'viewers/login.html', {
                'error': 'Email not found'
            })

        # Clear session and login with this email (allow login even with different device_id)
        request.session.flush()
        request.session['viewer_id'] = viewer.id
        
        # Update device_id if different (allows multi-device login)
        if viewer.device_identifier != device_id:
            viewer.device_identifier = device_id
            viewer.save()
        
        return redirect('viewer_dashboard')

    return render(request, 'viewers/login.html')