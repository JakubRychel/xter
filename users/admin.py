from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional information', {'fields': ('displayed_name', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional information', {'fields': ('displayed_name', 'bio')}),
    )

admin.site.register(User, CustomUserAdmin)