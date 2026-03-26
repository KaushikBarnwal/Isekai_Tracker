import logging
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from tracker.models import PendingStory
from quests.generator import generate_isekai_chapter

logger = logging.getLogger(__name__)

# GROQ free tier: 15 RPM = one request every 4 seconds minimum.
# Using 4 s keeps us well within the limit without the old 30 s over-wait.
GROQ_RATE_LIMIT_SLEEP = 4

class Command(BaseCommand):
    help = 'Processes pending stories that are due for generation'

    def handle(self, *args, **options):
        now = timezone.now()
        # Find all pending stories that are due
        pending_stories = PendingStory.objects.filter(
            is_processed=False,
            scheduled_time__lte=now
        ).order_by('scheduled_time')

        if not pending_stories.exists():
            self.stdout.write(self.style.SUCCESS('No pending stories to process.'))
            logger.info("process_stories: no pending stories due, exiting")
            return

        total = pending_stories.count()
        logger.info("process_stories: found %d pending story/stories to process", total)

        for idx, pending_story in enumerate(pending_stories, start=1):
            username = pending_story.player.user.username
            self.stdout.write(
                f"[{idx}/{total}] Processing story for {username} (Level: {pending_story.target_level})"
            )
            logger.info(
                "process_stories: starting story id=%d for player=%s level=%s",
                pending_story.id, username, pending_story.target_level,
            )

            t0 = time.monotonic()
            try:
                from datetime import date as date_class     # Parse date if necessary
                parsed_date = date_class.fromisoformat(pending_story.story_date) if pending_story.story_date else None
                found_item = None                           # Find item if necessary
                if pending_story.found_item_name:
                    from players.models import Item
                    found_item = Item.objects.filter(name=pending_story.found_item_name).first()

                generate_isekai_chapter(                # Call generator centrally and synchronously
                    player_id=pending_story.player.id,
                    steps=pending_story.steps,
                    exp_gained=pending_story.exp_gained,
                    leveled_up=pending_story.leveled_up,
                    target_level=pending_story.target_level,
                    found_item=found_item,
                    story_date=parsed_date,
                )

                pending_story.is_processed = True           # Mark processed
                pending_story.save()

                elapsed = time.monotonic() - t0
                self.stdout.write(self.style.SUCCESS(
                    f"  + Successfully generated story for {username} in {elapsed:.1f}s."
                ))
                logger.info(
                    "process_stories: completed story id=%d for player=%s in %.2fs",
                    pending_story.id, username, elapsed,
                )

            except Exception as e:
                elapsed = time.monotonic() - t0
                self.stdout.write(self.style.ERROR(
                    f"  x Error processing story ID {pending_story.id} after {elapsed:.1f}s: {str(e)}"
                ))
                logger.error(
                    "process_stories: error on story id=%d for player=%s after %.2fs: %s",
                    pending_story.id, username, elapsed, e, exc_info=True,
                )

            finally:
                # Always sleep between stories to respect GROQ rate limits.
                # Free tier allows 15 RPM — 4 s is the minimum safe interval.
                if idx < total:
                    self.stdout.write(
                        f"  ~ Sleeping {GROQ_RATE_LIMIT_SLEEP}s to respect GROQ rate limits..."
                    )
                    time.sleep(GROQ_RATE_LIMIT_SLEEP)

        logger.info("process_stories: finished processing %d stories", total)
