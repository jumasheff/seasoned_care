from datetime import datetime

from django.db import models


class Appointment(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} on {self.date} at {self.time}"


def create_appointment(json_object):
    try:
        name = json_object["name"]
        date_str = json_object["date"]
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        time_str = json_object["time"]
        time = datetime.strptime(time_str, "%H:%M").time()
        description = json_object["description"]
        obj = Appointment.objects.create(
            name=name, date=date, time=time, description=description
        )
        return obj
    except Exception as e:
        print("Exception in create_appointment: ", e)
        raise ValueError(e)
