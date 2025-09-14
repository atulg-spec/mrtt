from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from earning.utils import check_and_award_levels  # wherever your function is located

User = get_user_model()

class Command(BaseCommand):
    help = "Check and award levels for all users"

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        total_users = users.count()
        self.stdout.write(f"Found {total_users} users. Processing...")

        for idx, user in enumerate(users, start=1):
            try:
                check_and_award_levels(user)
                self.stdout.write(self.style.SUCCESS(f"[{idx}/{total_users}] Processed user {user.id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[{idx}/{total_users}] Error processing user {user.id}: {e}"))

        self.stdout.write(self.style.SUCCESS("All users processed successfully."))
