from django.contrib.gis.db import models
from django.core.exceptions import ValidationError

# User, Match, GroundReview는 문자열 참조로 처리
from newsfeed.models.newsfeed import NewsfeedPost

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("scheduled", "Scheduled"),
    ("ongoing", "Ongoing"),
    ("completed", "Completed"),
    ("canceled", "Canceled"),
]

class SportsGround(models.Model):
    name = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to='sportsgrounds/photos/', null=True, blank=True)
    location = models.PointField()
    description = models.TextField(blank=True, null=True)
    support = models.TextField(blank=True, null=True)
    rules = models.TextField(blank=True, null=True)
    opening_hours = models.JSONField(blank=True, null=True)
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="owned_ground")  # 문자열 참조

    reviews = models.ManyToManyField('matchmaking.GroundReview', related_name='ground_reviews', blank=True)  # 문자열 참조
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    followers = models.ManyToManyField('accounts.User', related_name="followed_grounds", blank=True)  # 문자열 참조

    def __str__(self):
        return self.name
    
    def is_owner(self, user):
        return self.owner == user

    def calculate_average_rating(self):
        total_reviews = self.reviews.count()
        if total_reviews > 0:
            total_quality = sum(review.quality for review in self.reviews.all() if 1 <= review.quality <= 5)
            total_safety = sum(review.safety for review in self.reviews.all() if 1 <= review.safety <= 5)
            total_support = sum(review.support for review in self.reviews.all() if 1 <= review.support <= 5)

            if total_quality == 0 or total_safety == 0 or total_support == 0:
                raise ValidationError("Invalid review data detected.")

            avg_quality = total_quality / total_reviews
            avg_safety = total_safety / total_reviews
            avg_support = total_support / total_reviews

            self.average_rating = (avg_quality + avg_safety + avg_support) / 3
        else:
            self.average_rating = 0.0
        self.save()

    def get_matches(self):
        return models.get_model('matchmaking', 'Match').objects.filter(sports_ground=self)  # 문자열 참조

    def follow_ground(self, user):
        if user not in self.followers.all():
            self.followers.add(user)
            self.save()
            self.update_newsfeed_for_followers(user)

    def unfollow_ground(self, user):
        if user in self.followers.all():
            self.followers.remove(user)
            self.save()

    def update_newsfeed_for_followers(self, user):
        matches = self.get_matches()
        for match in matches:
            NewsfeedPost.objects.create(
                newsfeed=user.newsfeed,
                post_type="match",
                post_id=match.id,
                post_content=f"New match scheduled at {self.name}."
            )


class Booking(models.Model):
    sports_ground = models.ForeignKey(SportsGround, on_delete=models.CASCADE, related_name="bookings")
    facility = models.ForeignKey('Facilities', on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="bookings")  # 문자열 참조
    time_slot = models.ForeignKey('TimeSlot', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Booking at {self.sports_ground.name} by {self.user.username}"

    def confirm_booking(self, owner):
        if not self.sports_ground.is_owner(owner):
            raise PermissionError("You do not have permission to confirm this booking.")
        
        if self.time_slot.is_reserved:
            raise ValidationError("This time slot is already reserved.")

        self.status = "scheduled"
        self.time_slot.reserve(self.match)
        self.save()

        pending_matches = models.get_model('matchmaking', 'Match').objects.filter(  # 문자열 참조
            sports_ground=self.sports_ground,
            facility=self.facility,
            time_slot=self.time_slot,
            status="pending"
        )
        for match in pending_matches:
            match.status = "canceled"
            match.save()

    def decline_booking(self, owner):
        if not self.sports_ground.is_owner(owner):
            raise PermissionError("You do not have permission to decline this booking.")
        
        self.status = "canceled"
        self.save()

    def cancel_booking(self):
        if self.status == "scheduled":
            self.time_slot.is_reserved = False
            self.time_slot.save()
            self.status = "canceled"
            self.save()