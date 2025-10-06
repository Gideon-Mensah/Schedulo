from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Organization
import uuid
from datetime import date


# We will extend Django's built-in User model by add phone number to it
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

def user_avatar_path(instance, filename):
    # uploads to: media/avatars/<user_id>/<filename>
    return f"avatars/{instance.user_id}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)
    job_title = models.CharField(max_length=64, blank=True)
    bio = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self):
        return f"{self.user} ({self.organization or 'No org'})"


# Auto-create + keep a profile for every user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # ensure profile exists
        Profile.objects.get_or_create(user=instance)

class OrgMembership(models.Model):
    ROLE_CHOICES = (("owner","Owner"),("manager","Manager"),("staff","Staff"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="org_memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")

    class Meta:
        unique_together = ("user","organization")


class IDCard(models.Model):
    """ID Card model for user identification"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="id_cards")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="id_cards")
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(default=date.today)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    blood_type = models.CharField(max_length=5, blank=True, help_text="e.g., A+, O-, etc.")
    access_level = models.CharField(max_length=50, default="Standard", help_text="Access permissions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'organization')
        ordering = ['-created_at']

    def __str__(self):
        return f"ID Card - {self.user.get_full_name() or self.user.username} ({self.organization.name})"

    def save(self, *args, **kwargs):
        # Auto-generate employee ID if not provided
        if not self.employee_id:
            # Format: ORG-YEAR-XXXX (e.g., DELAALA-2025-0001)
            org_prefix = self.organization.name[:8].upper().replace(' ', '')
            year = date.today().year
            
            # Get the last employee ID for this organization this year
            last_card = IDCard.objects.filter(
                organization=self.organization,
                employee_id__startswith=f"{org_prefix}-{year}-"
            ).order_by('-employee_id').first()
            
            if last_card and last_card.employee_id:
                try:
                    last_number = int(last_card.employee_id.split('-')[-1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    next_number = 1
            else:
                next_number = 1
            
            self.employee_id = f"{org_prefix}-{year}-{next_number:04d}"
        
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def job_title(self):
        profile = getattr(self.user, 'profile', None)
        return profile.job_title if profile else 'Employee'

    @property
    def avatar_url(self):
        profile = getattr(self.user, 'profile', None)
        if profile and profile.avatar:
            return profile.avatar.url
        return None

    @property
    def phone_number(self):
        profile = getattr(self.user, 'profile', None)
        return profile.phone if profile else self.user.phone_number
