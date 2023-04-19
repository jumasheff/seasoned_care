from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "time", "description", "created_at")
    list_filter = ("name", "date", "time", "description", "created_at")
    search_fields = ("name", "date", "time", "description", "created_at")
    ordering = ("name", "date", "time", "description", "created_at")
    date_hierarchy = "date"
