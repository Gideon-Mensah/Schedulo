# shifts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ShiftBooking
from .emails import send_booking_email

@receiver(post_save, sender=ShiftBooking)
def notify_user_on_booking_create(sender, instance: ShiftBooking, created, **kwargs):
    # Only on creation, not every update (e.g., clock in/out)
    if created:
        send_booking_email(instance)
