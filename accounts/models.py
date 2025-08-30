from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    def __str__(self):
        return f"Profile({self.user})"

# Auto-create + keep a profile for every user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # ensure profile exists
        Profile.objects.get_or_create(user=instance)
