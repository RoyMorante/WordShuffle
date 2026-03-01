from django.db import models
from django.contrib.auth.models import User
from apps.events.models import Event


class Exhibitor(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='exhibitors')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    booth_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Booth {self.booth_number})"