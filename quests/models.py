from django.db import models
from django.utils.timezone import localdate
from players.models import PlayerProfile

# Create your models here.
class DailyStory(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="stories")
    date = models.DateField(default=localdate)
    content = models.TextField()
    memory_summary = models.CharField(max_length=500)
    image_url = models.URLField(blank=True, null=True)
    level_at_time = models.PositiveIntegerField(default=1)
    # Arc & Journey Metadata
    world_region = models.CharField(max_length=100, blank=True, null=True)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    steps_taken = models.PositiveIntegerField(default=0)
    exp_gained = models.PositiveIntegerField(default=0)
    found_item_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Day {self.date} for {self.player.user.username}"

