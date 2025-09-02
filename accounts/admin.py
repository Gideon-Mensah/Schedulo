from django.contrib import admin
from .models import Profile

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email' , 'phone_number', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_staff', 'is_active')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization")
    list_filter = ("organization",)
    search_fields = ("user__username", "user__email", "organization__name")


# Register your models here.
admin.site.register(User, UserAdmin)
