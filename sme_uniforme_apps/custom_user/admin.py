from django.contrib import admin

from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {"fields": ("email", "password", 'validado')}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    list_display = ("email", "first_name", "last_name", "is_staff", "validado")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    list_filter = ("validado",)
