import math
import logging
from django.core.management.base import BaseCommand
from django.db.models import Sum
from players.models import PlayerProfile
from quests.models import DailyStory
from tracker.constants import BASE_XP_REQ, LEVEL_EXPONENT

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Audits and fixes discrepancies between total EXP in chronicles and the player dashboard.'

    def calculate_required_exp(self, current_level):
        return math.floor(BASE_XP_REQ * (current_level ** LEVEL_EXPONENT))

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("  🕵️‍♂️ EXP AUDIT & FIX — Cross-checking Chronicles vs Dashboard")
        self.stdout.write("=" * 60 + "\n")

        players = PlayerProfile.objects.all()

        for player in players:
            self.stdout.write(f"\n👤 Player: {player.user.username}")
            
            # 1. Calculate true total EXP from dashboard (Level + Leftover EXP)
            true_total_exp = player.exp
            for lvl in range(1, player.level):
                true_total_exp += self.calculate_required_exp(lvl)
            
            # 2. Calculate sum of EXP from chronicles (DailyStory)
            # Since multiple stories on the same day (due to multiple level-ups) 
            # all received the SAME exp_gained value (which was a bug), 
            # we need to find duplicates and fix them.
            
            stories = DailyStory.objects.filter(player=player).order_by('date', 'id')
            
            chronicles_total_exp = 0
            processed_dates = set()
            
            fixes_made = 0
            
            for story in stories:
                # If we already recorded the EXP for this date, the subsequent stories 
                # for the SAME day shouldn't add the full day's EXP again.
                if story.date in processed_dates:
                    if story.exp_gained > 0:
                        self.stdout.write(self.style.WARNING(
                            f"  ⚠️ Duplicate EXP found on {story.date}: removing {story.exp_gained} EXP from extra story chapter."
                        ))
                        # Fix the duplicate in the database
                        story.exp_gained = 0
                        story.save()
                        fixes_made += 1
                else:
                    chronicles_total_exp += story.exp_gained
                    processed_dates.add(story.date)

            # Wait, what about pending stories?
            from tracker.models import PendingStory
            pending = PendingStory.objects.filter(player=player, is_processed=False).order_by('story_date', 'id')
            pending_dates = set()
            for p_story in pending:
                # Same logic for pending stories
                if p_story.story_date in pending_dates or p_story.story_date in [str(d) for d in processed_dates]:
                    if p_story.exp_gained > 0:
                        self.stdout.write(self.style.WARNING(
                            f"  ⚠️ Duplicate EXP found in PendingStory for {p_story.story_date}: removing {p_story.exp_gained} EXP."
                        ))
                        p_story.exp_gained = 0
                        p_story.save()
                        fixes_made += 1
                else:
                    chronicles_total_exp += p_story.exp_gained
                    pending_dates.add(p_story.story_date)

            self.stdout.write(f"  📊 Dashboard Total EXP (True): {true_total_exp:,}")
            self.stdout.write(f"  📖 Chronicles Total EXP (Sum): {chronicles_total_exp:,}")
            
            diff = true_total_exp - chronicles_total_exp
            
            if diff == 0:
                self.stdout.write(self.style.SUCCESS("  ✅ Perfectly synced! No dashboard fixes needed."))
            else:
                self.stdout.write(self.style.WARNING(f"  ❌ Discrepancy found! Dashboard is off by {diff:,} EXP. Fixing dashboard..."))
                
                # We trust the chronicles_total_exp as the ground truth of all awarded EXP.
                # Let's recalculate the correct level and leftover EXP from 0.
                correct_level = 1
                remaining_exp = chronicles_total_exp
                
                while True:
                    req_exp = self.calculate_required_exp(correct_level)
                    if remaining_exp >= req_exp:
                        remaining_exp -= req_exp
                        correct_level += 1
                    else:
                        break
                
                # Update player stats
                player.level = correct_level
                player.exp = remaining_exp
                player.base_hp = 100 + ((correct_level - 1) * 10)
                player.base_mana = 20 + ((correct_level - 1) * 2)
                
                # Update region if necessary based on new level
                from tracker.constants import WORLD_REGIONS
                # Find highest unlocked region
                highest_unlocked_lvl = 1
                for region_lvl in WORLD_REGIONS.keys():
                    if correct_level >= region_lvl and region_lvl >= highest_unlocked_lvl:
                        highest_unlocked_lvl = region_lvl
                
                new_zone = WORLD_REGIONS[highest_unlocked_lvl]
                player.current_location = new_zone["location"]
                player.world_region = new_zone["region"]
                
                player.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f"  🛠️ Dashboard Fixed! Player is now Level {player.level} with {player.exp} EXP."
                ))
            
            if fixes_made > 0:
                self.stdout.write(self.style.SUCCESS(f"  🛠️ Fixed {fixes_made} duplicate EXP entries in chronicles."))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("  ✅ AUDIT & FIX COMPLETE")
        self.stdout.write("=" * 60 + "\n")
