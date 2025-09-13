# shifts/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, time as dtime, timedelta
from datetime import datetime as dt, time as dtime
from django.utils import timezone
from core.models import TenantOwned
from core.managers import TenantManager

User = settings.AUTH_USER_MODEL

def _normalize_postcode(pc: str | None) -> str | None:
    """Uppercase and strip spaces so comparisons are consistent."""
    if not pc:
        return pc
    return pc.replace(" ", "").upper()


class Shift(TenantOwned):
    ROLE_CHOICES = [('Care','Care'),('Cleaning','Cleaning')]
    title = models.CharField(max_length=200, default="Untitled Shift")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    location = models.CharField(max_length=255)
    max_staff = models.IntegerField()
    allowed_postcode = models.CharField(max_length=16, null=True, blank=True)

    # 👇 managers
    all_objects = models.Manager()     # unfiltered (for admin, debugging)
    objects = TenantManager()          # tenant-scoped (for your app)

    def __str__(self):
        st = self.start_time.strftime("%H:%M") if self.start_time else "--:--"
        et = self.end_time.strftime("%H:%M") if self.end_time else "--:--"
        return f"{self.title} ({self.date} {st}-{et})"

    # ---- Capacity helpers ----
    def booked_count(self) -> int:
        return self.shiftbooking_set.count()

    def has_space(self) -> bool:
        return self.booked_count() < self.max_staff

    @property
    def booked_count_prop(self) -> int:
        return self.booked_count()

    @property
    def has_space_prop(self) -> bool:
        return self.has_space()

    # ---- Time helpers ----
    def _end_dt(self):
        t = self.end_time or self.start_time or dtime(23, 59, 59)
        naive = dt.combine(self.date, t)
        return timezone.make_aware(naive, timezone.get_current_timezone()) \
            if timezone.is_naive(naive) else naive

    @property
    def is_past(self) -> bool:
        return self._end_dt() <= timezone.now()

    def start_dt(self):
        t = self.start_time or dtime(0, 0, 0)
        naive = dt.combine(self.date, t)
        return timezone.make_aware(naive, timezone.get_current_timezone()) \
            if timezone.is_naive(naive) else naive

    def save(self, *args, **kwargs):
        self.allowed_postcode = _normalize_postcode(self.allowed_postcode)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("date", "start_time", "title")



class ShiftBooking(TenantOwned):
    from django.conf import settings
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name="bookings")
    booked_at = models.DateTimeField(auto_now_add=True)

    # Punches (store where + the postcode that was resolved by the server)
    clock_in_at = models.DateTimeField(null=True, blank=True)
    clock_in_lat = models.FloatField(null=True, blank=True)
    clock_in_lng = models.FloatField(null=True, blank=True)
    clock_in_postcode = models.CharField(max_length=16, null=True, blank=True)

    clock_out_at = models.DateTimeField(null=True, blank=True)
    clock_out_lat = models.FloatField(null=True, blank=True)
    clock_out_lng = models.FloatField(null=True, blank=True)
    clock_out_postcode = models.CharField(max_length=16, null=True, blank=True)

    # NEW: optional extras at clock-out
    clock_out_note = models.TextField(blank=True, default="")
    clock_out_supervisor_name = models.CharField(max_length=100, blank=True, default="")
    clock_out_signature = models.ImageField(upload_to="signatures/", null=True, blank=True)
    
    paid_at = models.DateTimeField(null=True, blank=True, db_index=True)

    
    admin_note = models.TextField(blank=True, null=True)
    
    objects = TenantManager()
    
    @property
    def is_completed(self) -> bool:
        return bool(self.clock_in_at and self.clock_out_at)

    @property
    def is_paid(self) -> bool:
        return self.paid_at is not None
    
    def mark_paid(self):
        if not self.paid_at:
            self.paid_at = timezone.now()
            self.save(update_fields=["paid_at"])

    class Meta:
        unique_together = ('user', 'shift')  # Prevent double bookings

    def __str__(self):
        return f"{self.user} booked {self.shift}"

    # ---- Clock rules (time window only; postcode/location is enforced in views) ----
    def can_clock_in(self, now=None) -> bool:
        if self.clock_in_at:
            return False
        now = now or timezone.localtime()
        if self.shift.date != now.date():
            return False

        if not self.shift.start_time:
            return True  # no start time configured; allow (tune as needed)

        start_dt = datetime.combine(self.shift.date, self.shift.start_time)
        if timezone.is_naive(start_dt):
            start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())

        return (start_dt - timedelta(minutes=15)) <= now <= (start_dt + timedelta(minutes=30))

    def can_clock_out(self, now=None) -> bool:
        if not self.clock_in_at or self.clock_out_at:
            return False
        now = now or timezone.localtime()
        if self.shift.date != now.date():
            return False

        if self.shift.end_time:
            end_dt = datetime.combine(self.shift.date, self.shift.end_time)
            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt, timezone.get_current_timezone())
            # Allow up to 6 hours after scheduled end
            return self.clock_in_at <= now <= (end_dt + timedelta(hours=6))

        # If no end time, allow any time after clock-in on the same day
        return now >= self.clock_in_at
    
# Compliance
class ComplianceDocType(models.Model):
    name = models.CharField(max_length=120, unique=True)
    requires_expiry = models.BooleanField(default=True)
    default_validity_days = models.PositiveIntegerField(null=True, blank=True, help_text="Optional hint for admins.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


STATUS_CHOICES = (
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
)

def compliance_upload_path(instance, filename):
    # MEDIA_ROOT/compliance/<user_id>/<type>/<filename>
    safe_type = (instance.doc_type.name or "document").replace(" ", "_").lower()
    return f"compliance/{instance.user_id}/{safe_type}/{filename}"

class ComplianceDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="compliance_docs")
    doc_type = models.ForeignKey(ComplianceDocType, on_delete=models.PROTECT, related_name="documents")
    file = models.FileField(upload_to=compliance_upload_path)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="approved")
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_compliance_docs")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.user} – {self.doc_type.name}"

    @property
    def is_expired(self):
        return bool(self.expiry_date and self.expiry_date < timezone.localdate())

    @property
    def days_left(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.localdate()).days
    
# Audit trail could be added here if desired

class AuditAction(models.TextChoices):
    SHIFT_CREATED       = "shift_created", "Shift created"
    SHIFT_UPDATED       = "shift_updated", "Shift updated"
    SHIFT_DELETED       = "shift_deleted", "Shift deleted"

    BOOKING_CREATED     = "booking_created", "Booking created"          # user self-book or admin assign
    BOOKING_CANCELLED   = "booking_cancelled", "Booking cancelled"
    BOOKING_NO_SHOW     = "booking_no_show", "Marked as no-show"

    CLOCK_IN            = "clock_in", "Clock in"
    CLOCK_OUT           = "clock_out", "Clock out"

    STATUS_OVERRIDE     = "status_override", "Status override"          # admin forced clock in/out etc.
    NOTES_UPDATED       = "notes_updated", "Notes updated"

class AuditLog(models.Model):
    at = models.DateTimeField(default=timezone.now, db_index=True)

    # who did it (actor) — may be null if system
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="audit_events",
    )

    # “about whom” (e.g., the staff assigned/affected)
    subject = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="audit_subject_events",
    )

    action = models.CharField(max_length=50, choices=AuditAction.choices, db_index=True)

    # scope / context
    shift = models.ForeignKey("shifts.Shift", null=True, blank=True, on_delete=models.SET_NULL)
    booking = models.ForeignKey("shifts.ShiftBooking", null=True, blank=True, on_delete=models.SET_NULL)

    # free text and structured extras
    message = models.TextField(blank=True)
    extra = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ["-at"]

    def __str__(self):
        target = self.booking or self.shift or "-"
        who = self.actor or "system"
        return f"[{self.at:%Y-%m-%d %H:%M}] {who} {self.action} {target}"