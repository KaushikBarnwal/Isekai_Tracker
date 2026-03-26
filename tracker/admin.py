from django.contrib import admin
from .models import DailyStepLog

# Register your models here.
@admin.register(DailyStepLog)
class DailyStepLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'steps', 'is_processed')
    list_filter = ('is_processed', 'date')