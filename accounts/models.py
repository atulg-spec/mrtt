from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.PositiveIntegerField(blank=True, null=True)
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile')
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    region_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    timezone = models.CharField(max_length=100, blank=True, null=True)
    isp = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    registration_fee_paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)

    referral_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4()).replace('-', '')[:10]  # Generate unique referral code
        super().save(*args, **kwargs)

    def getCommunity(self):
        """
        Fetches the community (users directly or indirectly referred by this user).
        """
        community = set()  # Using a set to avoid duplicates

        def traverse(user):
            if user not in community:
                community.add(user)
                # Traverse all users referred by 'user'
                for referral in user.referrals.all():
                    traverse(referral)

        traverse(self)
        return community


    def __str__(self):
        return self.username