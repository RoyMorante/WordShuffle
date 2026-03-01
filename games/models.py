from django.db import models
from django.utils import timezone
from apps.events.models import Event
from apps.viewers.models import Viewer


# ==========================================
# GAME CONFIGURATION
# ==========================================

class GameConfig(models.Model):

    GAME_TYPE_CHOICES = (
        ('memory', 'Memory Game'),
        ('word_shuffle', 'Word Shuffle'),
        ('quiz', 'Quiz'),
        ('reaction', 'Reaction Game'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    game_type = models.CharField(max_length=50, choices=GAME_TYPE_CHOICES)

    title = models.CharField(max_length=255)

    default_time_limit = models.IntegerField(default=60)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# Allows levels like:
# Easy
# Medium
# Hard
# Level 1, 2, 3, etc.
# Each level can have different time limits, max scores, etc.
class GameLevel(models.Model):

    game_config = models.ForeignKey(GameConfig, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    time_limit_seconds = models.IntegerField()
    max_score = models.IntegerField()

    difficulty_order = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.game_config.title} - {self.name}"
    
    

class GameContent(models.Model):

    CONTENT_TYPE_CHOICES = (
        ('word', 'Word'),
        ('question', 'Question'),
        ('memory_pair', 'Memory Pair'),
        ('custom_data', 'Custom Data'),
    )

    game_config = models.ForeignKey(GameConfig, on_delete=models.CASCADE)
    level = models.ForeignKey(GameLevel, on_delete=models.CASCADE)

    content_type = models.CharField(max_length=30, choices=CONTENT_TYPE_CHOICES)

    data = models.JSONField()

    points = models.IntegerField(default=10)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.game_config.title} - {self.content_type}"
    
# ==========================================
# GAME SESSION (Controlled by Staff)
# ==========================================

class GameSession(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    game_config = models.ForeignKey(GameConfig, on_delete=models.CASCADE)
    level = models.ForeignKey(GameLevel, on_delete=models.CASCADE)

    started_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Session {self.id}"


# ==========================================
# GAME ATTEMPT (PER VIEWER PLAY)
# ==========================================

class GameAttempt(models.Model):

    session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    viewer = models.ForeignKey(Viewer, on_delete=models.CASCADE)

    score = models.IntegerField()
    time_spent_seconds = models.IntegerField()

    raw_answers = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'viewer')
    
    

    
    
# WHAT THIS ENABLES

# Feature	Supported?
# Add unlimited words	✅
# Add unlimited quiz questions	✅
# Add multiple difficulty levels	✅
# Randomize content per session	✅
# Change time per level	✅
# Add new game types later	✅
# Multi-round competitions	✅

# EXAMPLE: Word Shuffle with Levels
# Level	Time	Words
# Easy	60s	CAT, DOG
# Medium	45s	PYTHON, SYSTEM
# Hard	30s	INNOVATION, TRANSFORMATION

# Staff selects level → system loads content dynamically.

# EXAMPLE: LMS Quiz
# Admin adds 50 questions.

# Session can:
# Randomly pick 10
# Shuffle order
# Auto grade

# ADVANTAGE
# This becomes a Mini LMS + Game Engine inside your raffle system.
# Fully configurable.