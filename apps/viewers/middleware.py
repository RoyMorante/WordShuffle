from .models import Viewer


class ViewerAutoLoginMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        viewer_id = request.session.get('viewer_id')

        if viewer_id:
            try:
                request.viewer = Viewer.objects.get(id=viewer_id)
            except Viewer.DoesNotExist:
                request.viewer = None
        else:
            request.viewer = None

        return self.get_response(request)