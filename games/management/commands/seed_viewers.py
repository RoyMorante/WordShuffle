from django.core.management.base import BaseCommand
from apps.events.models import Event
from apps.viewers.models import Viewer


class Command(BaseCommand):
    help = 'Seed sample viewers for testing'

    def handle(self, *args, **options):
        from datetime import datetime, timedelta
        
        # Get or create an event
        event, _ = Event.objects.get_or_create(
            name='Tech Expo 2024',
            defaults={
                'description': 'Annual Technology Exhibition',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=1),
                'is_active': True,
            }
        )

        # Sample viewers
        viewers_data = [
            {
                'email': 'john.doe@example.com',
                'full_name': 'John Doe',
                'gender': 'male',
                'user_type': 'student',
                'department': 'Computer Science',
                'device_identifier': 'device_001',
            },
            {
                'email': 'jane.smith@example.com',
                'full_name': 'Jane Smith',
                'gender': 'female',
                'user_type': 'faculty',
                'department': 'Engineering',
                'device_identifier': 'device_002',
            },
            {
                'email': 'mike.johnson@example.com',
                'full_name': 'Mike Johnson',
                'gender': 'male',
                'user_type': 'employee',
                'department': 'IT',
                'device_identifier': 'device_003',
            },
            {
                'email': 'sarah.williams@example.com',
                'full_name': 'Sarah Williams',
                'gender': 'female',
                'user_type': 'student',
                'department': 'Information Technology',
                'device_identifier': 'device_004',
            },
            {
                'email': 'alex.brown@example.com',
                'full_name': 'Alex Brown',
                'gender': 'other',
                'user_type': 'others',
                'department': 'General',
                'device_identifier': 'device_005',
            },
        ]

        self.stdout.write("👥 Seeding Sample Viewers:\n")

        for viewer_data in viewers_data:
            viewer, created = Viewer.objects.get_or_create(
                event=event,
                email=viewer_data['email'],
                defaults={
                    'full_name': viewer_data['full_name'],
                    'gender': viewer_data['gender'],
                    'user_type': viewer_data['user_type'],
                    'department': viewer_data['department'],
                    'device_identifier': viewer_data['device_identifier'],
                }
            )
            status = "✓ Created" if created else "✓ Exists"
            self.stdout.write(f"{status}: {viewer.full_name} (ID: {viewer.id})")

        self.stdout.write("\n✅ Sample viewers seeded successfully!")
