from django.db import models
from apps.events.models import Event
from apps.viewers.models import Viewer
from apps.exhibitors.models import Exhibitor
from django.contrib.auth.models import User


class Visit(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    viewer = models.ForeignKey(Viewer, on_delete=models.CASCADE, related_name='visits')
    exhibitor = models.ForeignKey(Exhibitor, on_delete=models.CASCADE, related_name='visits')
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('viewer', 'exhibitor')
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['viewer']),
            models.Index(fields=['exhibitor']),
        ]

    def __str__(self):
        return f"{self.viewer.full_name} → {self.exhibitor.name}"