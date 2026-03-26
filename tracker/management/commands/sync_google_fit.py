import logging
import time
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
        # We run this at midnight, so we are calculating "yesterday's" steps.
        target_date = date.today() - timedelta(days=1)
        self.stdout.write(f"Starting Automated Sync for Date: {target_date}")
        logger.info("sync_google_fit started for date=%s", target_date)

        # Get all players connected to Google Fit
        connected_players = PlayerProfile.objects.exclude(
            google_refresh_token__isnull=True
        ).exclude(google_refresh_token__exact='')

        if not connected_players.exists():
            self.stdout.write(self.style.WARNING("No connected players found."))
            logger.warning("sync_google_fit: no connected players, exiting early")
            return

        success_count = 0
        error_count = 0

        for player in connected_players:
            username = player.user.username
            self.stdout.write(f"Syncing player: {username}")
            logger.info("sync_google_fit: fetching steps for player=%s", username)

            creds_dict = {
                'token': player.google_access_token,
                'refresh_token': player.google_refresh_token,
                'token_uri': player.google_token_uri,
                'client_id': player.google_client_id,
                'client_secret': player.google_client_secret,
            }

            t0 = time.monotonic()
            try:
                # 1. Fetch steps from FitService (which pulls the last 24h by default)
                real_steps = FitService.get_steps(creds_dict)
                elapsed = time.monotonic() - t0
                logger.info(
                    "sync_google_fit: Google Fit API returned %d steps for player=%s in %.2fs",
                    real_steps, username, elapsed,
                )

                # 2. Get or Create the Log for 'yesterday'
                step_log, created = DailyStepLog.objects.get_or_create(
                    user=player.user,
                    date=target_date,
                    defaults={'steps': real_steps, 'is_processed': False},
                )

                # 3. Fire the Engine if not processed
                if not step_log.is_processed:
                    step_log.steps = real_steps
                    step_log.save()
                    # This safely generates EXP and creates the PendingStory tasks
                    process_daily_steps(player, step_log)
                    self.stdout.write(self.style.SUCCESS(f"  + Success! Processed {real_steps} steps."))
                    logger.info("sync_google_fit: processed steps for player=%s", username)
                    success_count += 1
                else:
                    self.stdout.write(f"  - Skipped: {target_date} was already processed manually.")
                    logger.info("sync_google_fit: skipped already-processed date for player=%s", username)

            except TimeoutError as e:
                elapsed = time.monotonic() - t0
                msg = f"Google Fit API timed out after {elapsed:.1f}s"
                self.stdout.write(self.style.ERROR(f"  x Timeout for {username}: {msg}"))
                logger.error("sync_google_fit: timeout for player=%s after %.2fs: %s", username, elapsed, e)
                error_count += 1

            except Exception as e:
                elapsed = time.monotonic() - t0
                self.stdout.write(self.style.ERROR(f"  x Error for {username}: {str(e)}"))
                logger.error(
                    "sync_google_fit: unexpected error for player=%s after %.2fs: %s",
                    username, elapsed, e, exc_info=True,
                )
                error_count += 1

        self.stdout.write(f"\nSync Complete! Success: {success_count}, Errors: {error_count}")
        logger.info("sync_google_fit finished. success=%d errors=%d", success_count, error_count)
