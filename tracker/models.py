from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DailyStepLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    # Removed auto_now_add=True so can sync 'yesterday's' data if needed
    date = models.DateField()
    steps = models.PositiveIntegerField(default=0)
    distance_km = models.FloatField(default=0.0)
    is_processed = models.BooleanField(default=False)           # To mark if data is processed (checks new steps)
    story_text = models.TextField(null=True, blank=True)
    story_image_url = models.URLField(max_length=500, null=True, blank=True)
    level_at_time = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('user', 'date')                      # Ensure one data of log per user per day 

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.steps} steps, {self.distance_km} km"

class PendingStory(models.Model):
    player = models.ForeignKey('players.PlayerProfile', on_delete=models.CASCADE)
    steps = models.PositiveIntegerField()
    exp_gained = models.PositiveIntegerField()
    leveled_up = models.BooleanField(default=False)
    target_level = models.PositiveIntegerField(null=True, blank=True)
    story_date = models.CharField(max_length=50, null=True, blank=True)
    found_item_name = models.CharField(max_length=255, null=True, blank=True)
    scheduled_time = models.DateTimeField()
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PendingStory for {self.player.user.username} (Level {self.target_level}) - Scheduled: {self.scheduled_time}"
