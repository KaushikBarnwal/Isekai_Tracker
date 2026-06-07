import logging
from datetime import date
from django.core.management.base import BaseCommand
from players.models import PlayerProfile
from tracker.models import DailyStepLog
from tracker.services import process_daily_steps

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'One-time recovery: processes all unprocessed DailyStepLogs from past days'

    def handle(self, *args, **options):
        today = date.today()
        # Find all past logs that were never processed (today excluded — it hasn't ended yet)
        unprocessed_logs = DailyStepLog.objects.filter(
            is_processed=False,
            date__lt=today
        ).select_related('user').order_by('date')

        if not unprocessed_logs.exists():
            self.stdout.write(self.style.SUCCESS("No unprocessed past logs found. Nothing to recover."))
            return

        self.stdout.write(f"Found {unprocessed_logs.count()} unprocessed log(s) to recover:\n")
        
        success_count = 0
        error_count = 0

        for log in unprocessed_logs:
            self.stdout.write(f"  Processing: {log.user.username} | {log.date} | {log.steps} steps")
            try:
                player = PlayerProfile.objects.get(user=log.user)
                process_daily_steps(player, log)
                self.stdout.write(self.style.SUCCESS(
                    f"    ✅ Done! Player now Level {player.level} with {player.exp} EXP."
                ))
                success_count += 1
            except PlayerProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"    ❌ No PlayerProfile for {log.user.username}. Skipping."))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ❌ Error: {str(e)}"))
                error_count += 1

        self.stdout.write(f"\n🏁 Recovery Complete! Success: {success_count}, Errors: {error_count}")
        if success_count > 0:
            self.stdout.write(self.style.SUCCESS(
                "Run 'process_stories' next (or wait for the cron) to generate the AI stories."
            ))
