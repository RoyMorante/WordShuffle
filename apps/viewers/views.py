from django.shortcuts import render, redirect
from django.http import HttpResponse
from apps.events.models import Event
from .models import Viewer


def viewer_dashboard(request):

    viewer_id = request.session.get('viewer_id')

    if not viewer_id:
        return redirect('viewer_register')

    try:
        viewer = Viewer.objects.get(id=viewer_id)
    except Viewer.DoesNotExist:
        return redirect('viewer_register')

    return render(request, 'viewers/dashboard.html', {
        'viewer': viewer
    })
    
def viewer_register(request):

    event = Event.objects.filter(is_active=True).first()
    if not event:
        return HttpResponse("No active event")

    if request.method == 'POST':

        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')
        user_type = request.POST.get('user_type')
        department = request.POST.get('department')
        device_id = request.POST.get('device_id')

        viewer, created = Viewer.objects.get_or_create(
            email=email,
            device_identifier=device_id,
            defaults={
                'event': event,
                'full_name': full_name,
                'gender': gender,
                'user_type': user_type,
                'department': department,
            }
        )

        request.session['viewer_id'] = viewer.id
        return redirect('viewer_dashboard')

    return render(request, 'viewers/register.html')


