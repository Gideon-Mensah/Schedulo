from django.urls import path
from . import views

app_name = "shifts"  # <-- add this

urlpatterns = [
    path("ops/bookings/<int:booking_id>/clock-in/",  views.admin_clock_in_for_user,  name="admin_clock_in_for_user"),
    path("ops/bookings/<int:booking_id>/clock-out/", views.admin_clock_out_for_user, name="admin_clock_out_for_user"),
    path("ops/bookings/<int:booking_id>/cancel/",    views.admin_cancel_booking_admin, name="admin_cancel_booking_admin"),
    path("ops/bookings/<int:booking_id>/mark-paid/", views.admin_mark_booking_paid, name="admin_mark_booking_paid"),
]
