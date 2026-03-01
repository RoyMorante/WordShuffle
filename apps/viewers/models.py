from django.db import models
from apps.events.models import Event
import uuid


class Viewer(models.Model):

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('employee', 'Employee'),
        ('others', 'Others'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    user_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    department = models.CharField(max_length=255)

    device_identifier = models.CharField(max_length=255)

    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'device_identifier')
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"