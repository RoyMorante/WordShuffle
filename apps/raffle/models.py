from django.db import models
from apps.events.models import Event
from apps.viewers.models import Viewer


class RaffleSetting(models.Model):

    MODE_CHOICES = (
        ('draw', 'Standard Draw'),
        ('game', 'Game-Based'),
    )

    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    min_booth_required = models.IntegerField(default=1)
    game_threshold = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.event.name} - {self.mode}"


class RaffleEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    viewer = models.OneToOneField(Viewer, on_delete=models.CASCADE)
    game_score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['event']),
        ]

    def __str__(self):
        return f"{self.viewer.full_name}"


class RaffleWinner(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    raffle_entry = models.OneToOneField(RaffleEntry, on_delete=models.CASCADE)
    rank = models.IntegerField()
    drawn_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"Rank {self.rank} - {self.raffle_entry.viewer.full_name}"