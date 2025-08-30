from django.contrib import admin

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email' , 'phone_number', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_staff', 'is_active')


# Register your models here.
admin.site.register(User, UserAdmin)
