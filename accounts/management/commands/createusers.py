import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create 1000 fake users with random referrals'

    def handle(self, *args, **kwargs):
        for _ in range(1000):
            # Create user
            user = User.objects.create_user(
                username=f'fakeuser{_}',
                email=f'fakeuser{_}@example.com',
                password='password'  # You can set a default password here
            )

            # Assign random referral
            if User.objects.exists():
                referred_by = random.choice(User.objects.all())
                user.referred_by = referred_by
                user.save()

            self.stdout.write(self.style.SUCCESS(f'Created user {user.username}'))

        self.stdout.write(self.style.SUCCESS('Successfully created 1000 fake users'))
