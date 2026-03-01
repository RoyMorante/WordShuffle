from django.db import models
from django.core.exceptions import ValidationError


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.is_active:
            if Event.objects.filter(is_active=True).exclude(pk=self.pk).exists():
                raise ValidationError("Only one event can be active at a time.")

    def __str__(self):
        return self.name