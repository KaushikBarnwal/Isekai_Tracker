from django.contrib import admin
from .models import DailyStory

@admin.register(DailyStory)
class DailyStoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'date', 'memory_summary')