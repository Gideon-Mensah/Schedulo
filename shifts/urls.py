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
    path("request-holiday/", views.request_holiday, name="request_holiday"),
    path("my-holidays/", views.my_holidays, name="my_holidays"),
    path("cancel-holiday/<int:request_id>/", views.cancel_holiday_request, name="cancel_holiday_request"),
    
    # Admin holiday management
    path("admin/holidays/", views.admin_holiday_requests, name="admin_holiday_requests"),
    path("admin/holidays/dashboard/", views.admin_holiday_dashboard, name="admin_holiday_dashboard"),
    path("admin/holidays/add/", views.admin_add_holiday_request, name="admin_add_holiday_request"),
    path("admin/holidays/approve/<int:request_id>/", views.approve_holiday_request, name="approve_holiday_request"),
    path("admin/holidays/reject/<int:request_id>/", views.reject_holiday_request, name="reject_holiday_request"),
    
    # Admin user availability management
    path("admin/availabilities/", views.admin_user_availabilities, name="admin_user_availabilities"),
    path("admin/availabilities/add/", views.admin_add_user_availability, name="admin_add_user_availability"),
    path("admin/availabilities/delete/<int:availability_id>/", views.admin_delete_user_availability, name="admin_delete_user_availability"),
]
