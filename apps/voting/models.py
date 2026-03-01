from django.db import models
from apps.events.models import Event
from apps.viewers.models import Viewer
from apps.exhibitors.models import Exhibitor
from django.core.validators import MinValueValidator, MaxValueValidator


class Criteria(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Vote(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    viewer = models.OneToOneField(Viewer, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vote by {self.viewer.full_name}"


class VoteScore(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='scores')
    exhibitor = models.ForeignKey(Exhibitor, on_delete=models.CASCADE)
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ('vote', 'exhibitor', 'criteria')

    def __str__(self):
        return f"{self.exhibitor.name} - {self.criteria.name}"