from django.contrib import admin

from .models import HealthProfile


# Register your models here.
@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = ("get_username", "weight", "height", "age")

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email
