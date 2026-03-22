from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Customer, Dealer


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "name", "user_type", "is_staff", "is_active", "created_at")
    list_filter = ("user_type", "is_staff", "is_active", "is_google_login")
    search_fields = ("email", "name", "phone_number")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name", "phone_number", "address", "user_type", "is_google_login")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "name", "user_type", "is_staff", "is_active"),
        }),
    )


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__email", "user__name")
    ordering = ("-created_at",)


class DealerAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "created_at", "updated_at")
    list_filter = ("company_name",)
    search_fields = ("user__email", "user__name", "company_name")
    ordering = ("-created_at",)


admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Dealer, DealerAdmin)
