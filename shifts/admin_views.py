# shifts/admin_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db.models import Count, F, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from .models import Shift, ShiftBooking
from django.utils.dateparse import parse_date


User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def manage_shifts(request):
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    # --- Filters (GET) ---
    title_q   = (request.GET.get("title_q")   or "").strip()
    role_q    = (request.GET.get("role")      or "").strip()   # 'Care'|'Cleaning'|''
    start_q   = (request.GET.get("start")     or "").strip()   # 'YYYY-MM-DD'
    end_q     = (request.GET.get("end")       or "").strip()
    user_q    = (request.GET.get("user_q")    or "").strip()
    only_open = (request.GET.get("only_open") or "") == "1"     # checkbox

    # upcoming / future shifts base
    future_q = (
        Q(date__gt=today) |
        (Q(date=today) & (Q(end_time__gt=current_time) |
                          Q(end_time__isnull=True, start_time__gt=current_time) |
                          Q(start_time__isnull=True, end_time__isnull=True)))
    )
    shifts_qs = Shift.objects.filter(future_q)

    if title_q:
        shifts_qs = shifts_qs.filter(title__icontains=title_q)
    if role_q:
        shifts_qs = shifts_qs.filter(role=role_q)

    # date range
    sd = parse_date(start_q) if start_q else None
    ed = parse_date(end_q) if end_q else None
    if sd:
        shifts_qs = shifts_qs.filter(date__gte=sd)
    if ed:
        shifts_qs = shifts_qs.filter(date__lte=ed)

    shifts_qs = shifts_qs.annotate(booked_total=Count('shiftbooking'))

    if only_open:
        shifts_qs = shifts_qs.filter(booked_total__lt=F('max_staff'))

    upcoming_shifts = shifts_qs.order_by('date', 'start_time')[:20]

    # recent bookings
    recent_bookings = (
        ShiftBooking.objects
        .select_related("shift", "user")
        .order_by("-id")[:30]
    )

    # metrics
    total_shifts = Shift.objects.count()
    available_upcoming = Shift.objects.filter(future_q).count()
    booked_upcoming = (
        Shift.objects.filter(future_q)
        .annotate(booked_total=Count('shiftbooking'))
        .filter(booked_total__gte=1)
        .count()
    )
    total_users = get_user_model().objects.count()

    # users (with search)
    users_qs = get_user_model().objects.all()
    if user_q:
        users_qs = users_qs.filter(
            Q(username__icontains=user_q) |
            Q(first_name__icontains=user_q) |
            Q(last_name__icontains=user_q) |
            Q(email__icontains=user_q)
        )
    users = users_qs.order_by("username")[:500]

    return render(request, "admin/manage_shifts.html", {
        "upcoming_shifts": upcoming_shifts,
        "recent_bookings": recent_bookings,
        "total_shifts": total_shifts,
        "available_upcoming": available_upcoming,
        "booked_upcoming": booked_upcoming,
        "total_users": total_users,
        "users": users,

        # Echo filters back to template
        "title_q": title_q,
        "role_q": role_q,
        "start_q": start_q,
        "end_q": end_q,
        "only_open": only_open,
        "user_q": user_q,
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_book_for_user(request):
    user_id = request.POST.get("user_id")
    shift_id = request.POST.get("shift_id")

    if not user_id or not shift_id:
        messages.error(request, "Missing user or shift.")
        return redirect("admin_manage_shifts")

    user = get_object_or_404(User, id=user_id)
    shift = get_object_or_404(Shift, id=shift_id)

    # capacity check
    current_count = ShiftBooking.objects.filter(shift=shift).count()
    if current_count >= shift.max_staff:
        messages.warning(request, f"'{shift.title}' is already full.")
        return redirect("admin_manage_shifts")

    # no dupes
    if ShiftBooking.objects.filter(user=user, shift=shift).exists():
        messages.info(request, f"{user} is already booked on '{shift.title}'.")
        return redirect("admin_manage_shifts")

    ShiftBooking.objects.create(user=user, shift=shift)
    messages.success(request, f"Booked '{shift.title}' for {user}.")
    return redirect("admin_manage_shifts")


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_cancel_booking(request, booking_id):
    booking = get_object_or_404(ShiftBooking, id=booking_id)
    booking.delete()
    messages.success(request, f"Cancelled booking for {booking.user} on '{booking.shift.title}'.")
    return redirect("admin_manage_shifts")


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_clock_in_for_user(request, booking_id):
    """
    Admin can clock-in on behalf of a user.
    Optional: respect time window unless override checkbox is set.
    """
    booking = get_object_or_404(ShiftBooking, id=booking_id)
    override = request.POST.get("override") == "1"
    reason = (request.POST.get("reason") or "").strip()

    if booking.clock_in_at:
        messages.info(request, "This user is already clocked in.")
        return redirect("admin_manage_shifts")

    if not override and not booking.can_clock_in(now=timezone.localtime()):
        messages.warning(request, "Time window not valid for clock-in. Tick override to proceed.")
        return redirect("admin_manage_shifts")

    booking.clock_in_at = timezone.now()
    # Optionally save admin reason somewhere; if you add a field, store it.
    # booking.admin_note = reason
    booking.save()

    messages.success(request, "Clock-in recorded for the user.")
    return redirect("admin_manage_shifts")


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_clock_out_for_user(request, booking_id):
    booking = get_object_or_404(ShiftBooking, id=booking_id)
    override = request.POST.get("override") == "1"
    reason = (request.POST.get("reason") or "").strip()

    if booking.clock_out_at:
        messages.info(request, "This user is already clocked out.")
        return redirect("admin_manage_shifts")

    if not booking.clock_in_at and not override:
        messages.warning(request, "User has not clocked in. Tick override to proceed anyway.")
        return redirect("admin_manage_shifts")

    if not override and not booking.can_clock_out(now=timezone.localtime()):
        messages.warning(request, "Time window not valid for clock-out. Tick override to proceed.")
        return redirect("admin_manage_shifts")

    booking.clock_out_at = timezone.now()
    # Optionally save admin reason
    booking.admin_note = reason
    booking.save()

    messages.success(request, "Clock-out recorded for the user.")
    return redirect("admin_manage_shifts")
