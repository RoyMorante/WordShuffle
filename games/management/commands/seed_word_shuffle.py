from django.core.management.base import BaseCommand
from apps.events.models import Event
from games.models import GameConfig, GameLevel, GameContent


class Command(BaseCommand):
    help = 'Seed Word Shuffle game with sample data'

    def handle(self, *args, **options):
        from datetime import datetime, timedelta
        
        # Get the first active event
        event = Event.objects.filter(is_active=True).first()
        
        if not event:
            self.stdout.write(self.style.ERROR('No active event found!'))
            return
        
        self.stdout.write(f"Using event: {event.name} (ID: {event.id})")

        # Create Word Shuffle game config
        game_config, created = GameConfig.objects.get_or_create(
            event=event,
            game_type='word_shuffle',
            defaults={
                'title': 'Word Shuffle - Guess the Word',
                'default_time_limit': 60,
                'is_active': True,
            }
        )

        self.stdout.write(f"✓ Game Config: {game_config.title}")

        # Create difficulty levels
        levels_data = [
            {'name': 'Easy', 'time_limit': 60, 'max_score': 120},
            {'name': 'Medium', 'time_limit': 45, 'max_score': 120},
            {'name': 'Hard', 'time_limit': 30, 'max_score': 120},
        ]

        levels = {}
        for level_data in levels_data:
            level, created = GameLevel.objects.get_or_create(
                game_config=game_config,
                name=level_data['name'],
                defaults={
                    'time_limit_seconds': level_data['time_limit'],
                    'max_score': level_data['max_score'],
                    'difficulty_order': len(levels) + 1,
                }
            )
            levels[level_data['name']] = level
            status = "✓ Created" if created else "✓ Exists"
            self.stdout.write(f"  {status}: {level.name} ({level.time_limit_seconds}s)")

        # Easy level words
        easy_words = [
            {'word': 'CAT', 'points': 10},
            {'word': 'DOG', 'points': 10},
            {'word': 'PYTHON', 'points': 10},
            {'word': 'SYSTEM', 'points': 10},
            {'word': 'COMPUTER', 'points': 10},
            {'word': 'CODE', 'points': 10},
        ]

        # Medium level words
        medium_words = [
            {'word': 'INNOVATION', 'points': 10},
            {'word': 'TECHNOLOGY', 'points': 10},
            {'word': 'APPLICATION', 'points': 10},
            {'word': 'INTERFACE', 'points': 10},
            {'word': 'DATABASE', 'points': 10},
            {'word': 'ALGORITHM', 'points': 10},
        ]

        # Hard level words
        hard_words = [
            {'word': 'TRANSFORMATION', 'points': 10},
            {'word': 'ARCHITECTURE', 'points': 10},
            {'word': 'INFRASTRUCTURE', 'points': 10},
            {'word': 'OPTIMIZATION', 'points': 10},
            {'word': 'SYNCHRONIZATION', 'points': 10},
            {'word': 'AUTHENTICATION', 'points': 10},
        ]

        # Add words to each level
        self.stdout.write("\n📝 Adding Words to Levels:")
        
        for word_data in easy_words:
            GameContent.objects.get_or_create(
                game_config=game_config,
                level=levels['Easy'],
                content_type='word',
                data={'word': word_data['word']},
                defaults={
                    'points': word_data['points'],
                    'is_active': True,
                }
            )

        self.stdout.write(f"  ✓ Easy: {len(easy_words)} words added")

        for word_data in medium_words:
            GameContent.objects.get_or_create(
                game_config=game_config,
                level=levels['Medium'],
                content_type='word',
                data={'word': word_data['word']},
                defaults={
                    'points': word_data['points'],
                    'is_active': True,
                }
            )

        self.stdout.write(f"  ✓ Medium: {len(medium_words)} words added")

        for word_data in hard_words:
            GameContent.objects.get_or_create(
                game_config=game_config,
                level=levels['Hard'],
                content_type='word',
                data={'word': word_data['word']},
                defaults={
                    'points': word_data['points'],
                    'is_active': True,
                }
            )

        self.stdout.write(f"  ✓ Hard: {len(hard_words)} words added")

        self.stdout.write("\n✅ Word Shuffle game data seeded successfully!")
        self.stdout.write(f"\nGame Configuration:")
        self.stdout.write(f"  - Game Config ID: {game_config.id}")
        self.stdout.write(f"  - Event ID: {event.id}")
        self.stdout.write(f"  - Levels: {', '.join([l.name for l in levels.values()])}")
