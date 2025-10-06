# Schedulo_app/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from shifts import views as shift_views
from shifts.views import NoCacheLoginView
from shifts.views_audit import audit_log
from accounts import views as accounts_views

urlpatterns = [
    # Include shifts app (namespaced) — must be BEFORE admin.site.urls
    path("", include(("shifts.urls", "shifts"), namespace="shifts")),

    # Home & auth
    path("", shift_views.home, name="home"),
    path("home/", shift_views.home, name="home"),
    path("accounts/login/", NoCacheLoginView.as_view(template_name="login.html"), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", accounts_views.register, name="register"),
    path("accounts/profile/", accounts_views.profile_view, name="account_profile"),
    path("accounts/profile/edit/", accounts_views.profile_edit, name="account_profile_edit"),
    path("accounts/password_change/", accounts_views.AccountPasswordChangeView.as_view(), name="account_password_change"),
    path("accounts/password_change/done/", accounts_views.AccountPasswordChangeDoneView.as_view(), name="account_password_change_done"),
    
    # Include accounts app URLs for ID cards
    path("accounts/", include("accounts.urls")),

    # User shift flows
    path("available-shifts/", shift_views.available_shifts, name="available_shifts"),
    path("book-shift/<int:shift_id>/", shift_views.book_shift, name="book_shift"),
    path("my-bookings/", shift_views.my_bookings, name="my_bookings"),
    path("my-calendar/", shift_views.my_calendar, name="my_calendar"),
    path("completed-shifts/", shift_views.completed_shifts, name="completed_shifts"),
    path("past-shifts/", shift_views.past_shifts, name="past_shifts"),
    path("cancel-booking/<int:booking_id>/", shift_views.cancel_booking, name="cancel_booking"),
    path("clock-in/<int:booking_id>/", shift_views.clock_in, name="clock_in"),
    path("clock-out/<int:booking_id>/", shift_views.clock_out, name="clock_out"),
    path("my-paid-shifts/", shift_views.my_paid_shifts, name="my_paid_shifts"),

    # Admin pages
    path("admin/dashboard/", shift_views.admin_dashboard, name="admin_dashboard"),
    path("admin/manage-shifts/", shift_views.admin_manage_shifts, name="admin_manage_shifts"),
    path("list_shifts/", shift_views.list_shifts, name="list_shifts"),
    path("create-shift/", shift_views.create_shift, name="create_shift"),
    path("admin/users/", shift_views.admin_user_list, name="admin_user_list"),
    path("admin/users/create/", shift_views.admin_user_create, name="admin_user_create"),
    path("admin/users/<int:user_id>/send-reset/", shift_views.admin_user_send_reset, name="admin_user_send_reset"),

    # Admin actions used by Manage Shifts
    path("admin/manage-shifts/book/", shift_views.admin_book_for_user, name="admin_book_for_user"),
    path("admin/manage-shifts/booking/<int:booking_id>/cancel/", shift_views.admin_cancel_booking_admin, name="admin_cancel_booking_admin"),
    path("admin/manage-shifts/booking/<int:booking_id>/clock-in/", shift_views.admin_clock_in_for_user, name="admin_clock_in_for_user"),
    path("admin/manage-shifts/booking/<int:booking_id>/clock-out/", shift_views.admin_clock_out_for_user, name="admin_clock_out_for_user"),
    path("admin/bookings/<int:booking_id>/mark-paid/", shift_views.admin_mark_booking_paid, name="admin_mark_booking_paid"),

    # Reports & compliance
    path("reports/attendance/", shift_views.attendance_report, name="attendance_report"),
    path("admin/paid-bookings/", shift_views.admin_paid_bookings, name="admin_paid_bookings"),
    path("bookings/<int:booking_id>/mark-paid/", shift_views.admin_mark_paid, name="admin_mark_paid"),
    path("bookings/<int:booking_id>/unmark-paid/", shift_views.admin_unmark_paid, name="admin_unmark_paid"),
    path("admin/compliance/", shift_views.compliance_admin_upload, name="compliance_admin_upload"),
    path("accounts/compliance/", shift_views.my_compliance, name="my_compliance"),
    path("admin/audit/", audit_log, name="audit_log"),

    # Django admin — keep LAST
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
