from django.contrib import admin

from accounts.models import User, UserProfile


@admin.register(User)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "date_joined")
    search_fields = ("email", "first_name", "last_name", "date_joined")



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "date_of_birth")
    search_fields = ("user__email", "phone")
