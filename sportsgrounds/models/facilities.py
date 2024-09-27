from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from sportsgrounds.models.sports_ground import SportsGround

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("scheduled", "Scheduled"),
    ("ongoing", "Ongoing"),
    ("completed", "Completed"),
    ("canceled", "Canceled"),
]

class Facilities(models.Model):
    sports_ground = models.ForeignKey(SportsGround, on_delete=models.CASCADE, related_name='facilities')
    facility_name = models.CharField(max_length=255)
    facility_description = models.TextField()
    facility_price = models.DecimalField(max_digits=10, decimal_places=2)
    photo_url = models.ImageField(upload_to='facilities/photos/', null=True, blank=True)

    def __str__(self):
        return self.facility_name


class TimeSlot(models.Model):
    facility = models.ForeignKey(Facilities, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.facility.facility_name} - {self.start_time} to {self.end_time}"

    def reserve(self, match):
        if not match:
            raise ValidationError("Match instance is missing.")
        
        if not self.is_reserved:
            self.is_reserved = True
            self.save()
            match.status = "scheduled"
            match.time_slot = self
            match.save()
        else:
            raise ValidationError("This time slot is already reserved.")