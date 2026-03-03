from django.core.management.base import BaseCommand
from apps.events.models import Event
from apps.raffle.models import RaffleSetting


class Command(BaseCommand):
    help = 'Seed raffle settings for testing'

    def handle(self, *args, **options):
        # Get the Tech Expo 2024 event
        event = Event.objects.filter(name='Tech Expo 2024').first()
        
        if not event:
            self.stdout.write(self.style.ERROR('❌ Event "Tech Expo 2024" not found. Please seed viewers first.'))
            return
        
        # Create or update raffle settings
        raffle_setting, created = RaffleSetting.objects.get_or_create(
            event=event,
            defaults={
                'mode': 'game',  # Game-based raffle
                'min_booth_required': 1,
                'game_threshold': 0,
                'is_active': True,
            }
        )
        
        status = "✓ Created" if created else "✓ Updated"
        self.stdout.write(f"{status}: Raffle Setting for {event.name}")
        self.stdout.write(f"  - Mode: {raffle_setting.mode}")
        self.stdout.write(f"  - Active: {raffle_setting.is_active}")
        self.stdout.write("\n✅ Raffle settings seeded successfully!")
