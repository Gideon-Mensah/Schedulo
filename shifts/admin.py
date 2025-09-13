# shifts/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Shift, ShiftBooking
from .models import ComplianceDocument, ComplianceDocType
from django.contrib.auth.models import User
from django.contrib.auth.forms import AdminPasswordChangeForm

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "title", "date", "start_time", "end_time", "role",
        "location", "allowed_postcode", "max_staff", "booked_count_admin",
    )
    list_filter = ("role", "date")
    search_fields = ("title", "location", "allowed_postcode")
    ordering = ("-date", "start_time")

    def get_queryset(self, request):
        # Use the unfiltered manager so admin shows *all* shifts
        return Shift.all_objects.all()

    def booked_count_admin(self, obj):
        return obj.shiftbooking_set.count()
    booked_count_admin.short_description = "Booked"


@admin.register(ShiftBooking)
class ShiftBookingAdmin(admin.ModelAdmin):
    list_display = (
        "user", "shift", "shift_date", "clock_in_at", "clock_out_at",
        "clock_in_postcode", "clock_out_postcode",
        "clock_in_coords", "clock_out_coords", 
        "status_badge","id", "user", "shift", "clock_in_at",
        "clock_out_at", "paid_at"
    )
    list_filter = [
        ("shift__date", admin.DateFieldListFilter),
        "shift__role",
        "shift__date",
        "paid_at",
        ("clock_in_at", admin.DateFieldListFilter),
        ("clock_out_at", admin.DateFieldListFilter),
    ]
    
    search_fields = (
        "user__username", "user__first_name", "user__last_name",
        "shift__title", "shift__location",
        "clock_in_postcode", "clock_out_postcode",
    )
    readonly_fields = (
        "user", "shift", "booked_at",
        "clock_in_at", "clock_in_lat", "clock_in_lng", "clock_in_postcode",
        "clock_out_at", "clock_out_lat", "clock_out_lng", "clock_out_postcode",
    )
    date_hierarchy = "shift__date"
    ordering = ("-id",)

    actions = ["export_csv"]
    
    actions = ["mark_as_paid"]

    @admin.action(description="Mark selected bookings as paid")
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(clock_in_at__isnull=False, clock_out_at__isnull=False, paid_at__isnull=True) \
                          .update(paid_at=timezone.now())
        self.message_user(request, f"{updated} booking(s) marked as paid.")
    

    # Niceties for columns
    def shift_date(self, obj):
        return obj.shift.date

    def clock_in_coords(self, obj):
        if obj.clock_in_lat is None or obj.clock_in_lng is None:
            return "-"
        return f"{obj.clock_in_lat:.5f}, {obj.clock_in_lng:.5f}"

    def clock_out_coords(self, obj):
        if obj.clock_out_lat is None or obj.clock_out_lng is None:
            return "-"
        return f"{obj.clock_out_lat:.5f}, {obj.clock_out_lng:.5f}"

    def status_badge(self, obj):
        if obj.clock_in_at and obj.clock_out_at:
            color, txt = "#0a7", "Complete"
        elif obj.clock_in_at and not obj.clock_out_at:
            color, txt = "#f90", "In progress"
        else:
            color, txt = "#777", "Not started"
        return format_html('<span style="padding:.15rem .4rem;border-radius:.5rem;background:{};color:#fff;">{}</span>', color, txt)
    status_badge.short_description = "Status"

    # Simple CSV export
    def export_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="shift_bookings.csv"'
        writer = csv.writer(resp)
        writer.writerow([
            "ID", "User", "Shift", "Shift date", "Start", "End",
            "Clock in at", "Clock in postcode", "Clock in lat", "Clock in lng",
            "Clock out at", "Clock out postcode", "Clock out lat", "Clock out lng",
        ])
        for b in queryset.select_related("shift", "user"):
            s = b.shift
            writer.writerow([
                b.id, str(b.user), str(s), s.date, s.start_time, s.end_time,
                b.clock_in_at, b.clock_in_postcode, b.clock_in_lat, b.clock_in_lng,
                b.clock_out_at, b.clock_out_postcode, b.clock_out_lat, b.clock_out_lng,
            ])
        return resp
    export_csv.short_description = "Export selected to CSV"

# Compliance models admin can go here too if desired

@admin.register(ComplianceDocType)
class ComplianceDocTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "requires_expiry", "default_validity_days", "is_active")
    list_editable = ("requires_expiry", "default_validity_days", "is_active")
    search_fields = ("name",)

@admin.register(ComplianceDocument)
class ComplianceDocumentAdmin(admin.ModelAdmin):
    list_display = ("user", "doc_type", "status", "issue_date", "expiry_date", "uploaded_at")
    list_filter = ("status", "doc_type")
    search_fields = ("user__username", "user__first_name", "user__last_name", "doc_type__name")
    autocomplete_fields = ("user", "doc_type", "uploaded_by")




