from django.urls import path
from . import views

app_name = "shifts"  # <-- add this

urlpatterns = [
    # Existing admin patterns
    path("ops/bookings/<int:booking_id>/clock-in/",  views.admin_clock_in_for_user,  name="admin_clock_in_for_user"),
    path("ops/bookings/<int:booking_id>/clock-out/", views.admin_clock_out_for_user, name="admin_clock_out_for_user"),
    path("ops/bookings/<int:booking_id>/cancel/",    views.admin_cancel_booking_admin, name="admin_cancel_booking_admin"),
    path("ops/bookings/<int:booking_id>/mark-paid/", views.admin_mark_booking_paid, name="admin_mark_booking_paid"),
    
    # User availability management
    path("availability/", views.my_availability, name="my_availability"),
    path("availability/add/", views.add_availability, name="add_availability"),
    path("availability/<int:availability_id>/edit/", views.edit_availability, name="edit_availability"),
    path("availability/<int:availability_id>/delete/", views.delete_availability, name="delete_availability"),
    
    # Holiday management
    path("holidays/", views.my_holidays, name="my_holidays"),
    path("holidays/request/", views.request_holiday, name="request_holiday"),
    path("holidays/<int:request_id>/cancel/", views.cancel_holiday_request, name="cancel_holiday_request"),
    
    # Admin holiday management
    path("admin/holidays/", views.admin_holiday_requests, name="admin_holiday_requests"),
    path("admin/holidays/<int:request_id>/approve/", views.approve_holiday_request, name="approve_holiday_request"),
    path("admin/holidays/<int:request_id>/reject/", views.reject_holiday_request, name="reject_holiday_request"),
]
