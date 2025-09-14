# shifts/emails.py
from django.template.loader import render_to_string, select_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def _org_template_candidates(org_slug: str | None, name: str):
    candidates = []
    if org_slug:
        candidates.append(f"orgs/{org_slug}/emails/{name}")
    candidates.append(f"emails/{name}")
    return candidates

def _render_both(org_slug: str | None, ctx: dict, base: str):
    text_tmpl = select_template(_org_template_candidates(org_slug, f"{base}.txt"))
    text_body = text_tmpl.render(ctx)
    try:
        html_tmpl = select_template(_org_template_candidates(org_slug, f"{base}.html"))
        html_body = html_tmpl.render(ctx)
    except Exception:
        html_body = None
    return text_body, html_body

def _from_address_for_org(org):
    org_name = getattr(org, "email_sender_name", None) or getattr(org, "name", None) or "Schedulo"
    org_from = getattr(org, "email_from", None) or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")
    reply_to = [getattr(org, "email_reply_to", "")] if getattr(org, "email_reply_to", None) else []
    from_email = f"{org_name} <{org_from}>"
    return from_email, reply_to

def send_booking_email(booking):
    """
    Sends an email to the booked user when a ShiftBooking is created.
    """
    user  = booking.user
    shift = booking.shift
    org   = getattr(booking, "organization", None)
    org_name = getattr(org, "name", None) or "Schedulo"
    org_slug = getattr(org, "slug", None)
    time_bits = ""
    if getattr(shift, "start_time", None):
        end = getattr(shift, "end_time", None)
        time_bits = f" {shift.start_time}–{end}" if end else f" {shift.start_time}"
    subject = f"Booking Confirmed – {shift.title} ({shift.date}{time_bits})"
    ctx = {
        "user": user,
        "shift": shift,
        "booking": booking,
        "org_name": org_name,
    }
    text_body, html_body = _render_both(org_slug, ctx, "booking_user")
    from_email, reply_to = _from_address_for_org(org)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[user.email] if user.email else [],
        reply_to=reply_to,
    )
    if html_body:
        msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=True)
