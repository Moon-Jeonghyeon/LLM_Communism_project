from django.contrib import admin
from users.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = [
        (None, {"fields": ("username", "password")}),
        ("개인정보", {"fields": ("first_name", "last_name", "email")}),
        ("추가필드", {"fields": ("profile_image",)}),
        (
            "권한",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            }
        ),
        ("중요한 일정", {"fields": ("last_login", "joined_at")}),
    ]
    readonly_fields = ["joined_at"]