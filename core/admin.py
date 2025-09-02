from django.contrib import admin
from .models import Organization, Domain

# Register your models here.


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "organization", "is_active")
    list_filter = ("is_active",)
    search_fields = ("domain",)
