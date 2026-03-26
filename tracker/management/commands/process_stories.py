import logging
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from tracker.models import PendingStory
from quests.generator import generate_isekai_chapter

logger = logging.getLogger(__name__)

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
            return
            
        for pending_story in pending_stories:
            self.stdout.write(f"Processing story for {pending_story.player.user.username} (Level: {pending_story.target_level})")
            try:
                from datetime import date as date_class     # Parse date if necessary
                parsed_date = date_class.fromisoformat(pending_story.story_date) if pending_story.story_date else None
                found_item = None                           # Find item if necessary
                if pending_story.found_item_name:
                    from players.models import Item
                    found_item = Item.objects.filter(name=pending_story.found_item_name).first()
                generate_isekai_chapter(                    # Call generator centrally and synchronously
                    player_id=pending_story.player.id,
                    steps=pending_story.steps,
                    exp_gained=pending_story.exp_gained,
                    leveled_up=pending_story.leveled_up,
                    target_level=pending_story.target_level,
                    found_item=found_item,
                    story_date=parsed_date
                )
                pending_story.is_processed = True           # Mark processed
                pending_story.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully generated story for {pending_story.player.user.username}."))
                
                # Sleep to prevent GROQ API rate limits (Free Tier allows 15 RPM)
                self.stdout.write("Sleeping 4 seconds to respect GROQ rate limits...")
                time.sleep(4)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing story ID {pending_story.id}: {str(e)}"))
                self.stdout.write("Sleeping 4 seconds before trying the next one...")
                time.sleep(4)
