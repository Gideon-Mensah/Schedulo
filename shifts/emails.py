# shifts/emails.py
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_booking_email(booking):
    """
    Sends an email to the booked user when a ShiftBooking is created.
    """
    user = booking.user
    shift = booking.shift
    if not user.email:
        return  # nothing to send to

    ctx = {
        "user": user,
        "shift": shift,
        "booking": booking,
    }

    subject = render_to_string("emails/booking_user_subject.txt", ctx).strip()
    text_body = render_to_string("emails/booking_user.txt", ctx)
    html_body = render_to_string("emails/booking_user.html", ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=True)
