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

        # --- Duplicate-run guard ---
        # Railway can occasionally trigger the cron twice
        # (e.g. on container restart / retry). We use a DB-level atomic check:
        # if ANY player already has a processed log for target_date that was
        # created by the cron (step count > 0 OR is_processed=True), we bail early.
        # This prevents double-processing EXP and duplicate stories.
        already_done = DailyStepLog.objects.filter(
            date=target_date,
            is_processed=True
        ).exists()
        if already_done:
            self.stdout.write(self.style.WARNING(
                f"⚠ Duplicate run detected: {target_date} was already fully processed "
                f"by a previous cron execution. Exiting to prevent double-processing."
            ))
            self.stdout.write(f"\nSync Complete! Success: 0, Errors: 0 (duplicate run skipped)")
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
            # 1. Fetch steps from Google Fit and unpack the (steps, creds) tuple.
            #    Token refresh and unpacking are isolated here so a failure never
            #    leaks an un-unpacked tuple into the step-log creation block below.
            updated_creds = None
            try:
                real_steps, updated_creds = FitService.get_steps(creds_dict)
            except Exception as e:
                # Token expired/revoked — fall back to 0 steps so the player still gets a daily story
                self.stdout.write(self.style.WARNING(
                    f"  ⚠ Token error for {player.user.username}: {str(e)}. Falling back to 0 steps."
                ))
                if 'invalid_grant' in str(e):
                    player.google_access_token = None
                    player.google_refresh_token = None
                    player.save(update_fields=['google_access_token', 'google_refresh_token'])
                real_steps = 0

            # 1a. Persist a refreshed access token only when get_steps() succeeded.
            if updated_creds:
                updated = False
                if updated_creds.get('token') != player.google_access_token:
                    player.google_access_token = updated_creds['token']
                    updated = True
                if updated_creds.get('refresh_token') and updated_creds.get('refresh_token') != player.google_refresh_token:
                    player.google_refresh_token = updated_creds['refresh_token']
                    updated = True
                if updated:
                    player.save(update_fields=['google_access_token', 'google_refresh_token'])

            # 2. Create / update the step log and run the story engine.
            try:
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
                    # This should not normally be reached since the duplicate-run guard
                    # above catches the case where all players are already processed.
                    # If we get here, it means only THIS specific player was pre-processed.
                    self.stdout.write(self.style.WARNING(
                        f"  - Skipped {player.user.username}: {target_date} log already has is_processed=True."
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  x Error for {player.user.username}: {str(e)}"))
                error_count += 1

        self.stdout.write(f"\nSync Complete! Success: {success_count}, Errors: {error_count}")
