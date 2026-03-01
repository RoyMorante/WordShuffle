from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from apps.events.models import Event
from apps.viewers.models import Viewer
from apps.exhibitors.models import Exhibitor
from .models import Visit


@login_required
@require_POST
def scan_viewer(request):

    qr_token = request.POST.get('qr_token')

    if not qr_token:
        return JsonResponse({'error': 'QR token required'}, status=400)

    # Active event
    event = Event.objects.filter(is_active=True).first()
    if not event:
        return JsonResponse({'error': 'No active event'}, status=400)

    # Get exhibitor
    try:
        exhibitor = Exhibitor.objects.get(user=request.user, event=event)
    except Exhibitor.DoesNotExist:
        return JsonResponse({'error': 'Not authorized exhibitor'}, status=403)

    # Validate viewer
    try:
        viewer = Viewer.objects.filter(
            qr_token=qr_token,
            event=event
        ).only('id', 'full_name').first()

        if not viewer:
            return JsonResponse({'error': 'Invalid QR'}, status=404)
    except Viewer.DoesNotExist:
        return JsonResponse({'error': 'Invalid QR'}, status=404)

    # Prevent duplicate
    if Visit.objects.filter(viewer=viewer, exhibitor=exhibitor).exists():
        return JsonResponse({
            'status': 'duplicate',
            'message': 'Already scanned'
        })

    # Log visit
    Visit.objects.create(
        event=event,
        viewer=viewer,
        exhibitor=exhibitor,
        scanned_by=request.user
    )

    return JsonResponse({
        'status': 'success',
        'viewer': viewer.full_name
    })