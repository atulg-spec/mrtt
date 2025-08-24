from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,  # enough for country code like +919876543210
        blank=True,
        unique=True,
        null=True,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number')])
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

    aadhaar_number = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{12}$', 'Enter a valid 12-digit Aadhaar number')]
    )
    date_of_birth = models.DateField(blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True, unique=True)

    referral_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        if self.pan_number == "":
            self.pan_number = None
        if self.aadhaar_number == "":
            self.aadhaar_number = None
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
    
def selfie_upload_path(instance, filename):
    # e.g. selfies/<user_id>/2025/08/21/<filename>
    return f"selfies/{instance.user.id}/{timezone.now().strftime('%Y/%m/%d')}/{filename}"


class SelfieWithTree(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Verification"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    user = models.OneToOneField(   # one selfie per user
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tree_selfie"
    )
    selfie_image = models.ImageField(upload_to=selfie_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    rejection_reason = models.TextField(blank=True, null=True)  # optional feedback

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Selfie with Tree"
        verbose_name_plural = "Selfies with Trees"

    def __str__(self):
        return f"Selfie by {self.user} • {self.uploaded_at:%Y-%m-%d %H:%M}"

    def verify(self):
        """Mark selfie as verified."""
        self.status = "verified"
        self.rejection_reason = None
        self.save(update_fields=["status", "rejection_reason"])

    def reject(self, reason=None):
        """Reject selfie with an optional reason."""
        self.status = "rejected"
        self.rejection_reason = reason
        self.save(update_fields=["status", "rejection_reason"])

    def reupload(self, new_image):
        """Allow user to reupload if rejected."""
        if self.status == "rejected":
            self.selfie_image = new_image
            self.status = "pending"
            self.rejection_reason = None
            self.uploaded_at = timezone.now()
            self.save()
