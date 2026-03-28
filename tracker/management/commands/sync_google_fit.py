import logging
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from players.models import PlayerProfile
from tracker.models import DailyStepLog
from tracker.fit_service import FitService
from tracker.services import process_daily_steps

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetches Google Fit steps for all connected players for the past 24 hours'

    def handle(self, *args, **options):
        # Run at midnight, calculating yesterday's steps.
        target_date = date.today() - timedelta(days=1)
        self.stdout.write(f"Starting Automated Sync for Date: {target_date}")
        # Get all players connected to Google Fit
        connected_players = PlayerProfile.objects.exclude(google_refresh_token__isnull=True).exclude(google_refresh_token__exact='')
        if not connected_players.exists():
            self.stdout.write(self.style.WARNING("No connected players found."))
            return

        success_count = 0
        error_count = 0

        for player in connected_players:
            self.stdout.write(f"Syncing player: {player.user.username}")
            creds_dict = {
                'token': player.google_access_token,
                'refresh_token': player.google_refresh_token,
                'token_uri': player.google_token_uri,
                'client_id': player.google_client_id,
                'client_secret': player.google_client_secret,
            }
            # 1. Fetch steps from FitService (pulls the last 24h by default)
            try:
                real_steps, updated_creds = FitService.get_steps(creds_dict)
                # 1a. Persist a refreshed access token so the next sync doesn't fail
                if updated_creds.get('token') != player.google_access_token:
                    player.google_access_token = updated_creds['token']
                    player.save(update_fields=['google_access_token'])
            except Exception as e:
                # Token expired/revoked — fall back to 0 steps so the player still gets a daily story
                self.stdout.write(self.style.WARNING(
                    f"  ⚠ Token error for {player.user.username}: {str(e)}. Falling back to 0 steps."
                ))
                real_steps = 0

            try:
                # 2. Get or Create the Log for yesterday
                step_log, created = DailyStepLog.objects.get_or_create(
                    user=player.user,
                    date=target_date,
                    defaults={'steps': real_steps, 'is_processed': False}
                )
                # 3. Fire the Engine if not processed
                if not step_log.is_processed:
                    step_log.steps = real_steps
                    step_log.save()
                    # Safely generates EXP and creates the PendingStory tasks
                    process_daily_steps(player, step_log)
                    self.stdout.write(self.style.SUCCESS(f"  + Success! Processed {real_steps} steps."))
                    success_count += 1
                else:
                    self.stdout.write(f"  - Skipped: {target_date} was already processed manually.")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  x Error for {player.user.username}: {str(e)}"))
                error_count += 1

        self.stdout.write(f"\nSync Complete! Success: {success_count}, Errors: {error_count}")
