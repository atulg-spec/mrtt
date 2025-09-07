import random
import uuid
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker("en_IN")  # Indian context

class Command(BaseCommand):
    help = 'Create 1000 fake users with random referrals'

    def handle(self, *args, **kwargs):
        for i in range(1000):
            # Generate fake details
            username = fake.user_name() + str(i)
            email = fake.unique.email()
            phone_number = fake.msisdn()[:10]  # 10-digit number
            address_line_1 = fake.street_address()
            address_line_2 = fake.street_name()
            state = fake.state()
            country = "India"
            city = fake.city()
            zip_code = fake.postcode()
            dob = fake.date_of_birth(minimum_age=18, maximum_age=60)

            # Aadhaar (12-digit) and PAN (10-char alphanumeric)
            aadhaar_number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            pan_number = fake.bothify(text="?????#####").upper()

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",  # Default password
                phone_number=phone_number,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                state=state,
                country=country,
                city=city,
                zip_code=zip_code,
                date_of_birth=dob,
                aadhaar_number=aadhaar_number,
                pan_number=pan_number,
                registration_fee_paid=random.choice([True, False]),
                amount_paid=random.choice([None, round(random.uniform(100, 10000), 2)])
            )

            # Assign random referral (if at least 1 user exists)
            if User.objects.exists() and i > 0:
                referred_by = random.choice(User.objects.exclude(id=user.id))
                user.referred_by = referred_by
                user.save()

            self.stdout.write(self.style.SUCCESS(f"Created user {user.username}"))

        self.stdout.write(self.style.SUCCESS("Successfully created 1000 fake users"))
