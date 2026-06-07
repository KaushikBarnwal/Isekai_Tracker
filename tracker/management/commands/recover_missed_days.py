import math
import logging
from datetime import date
from django.core.management.base import BaseCommand
from django.db.models import Sum
from players.models import PlayerProfile, InventoryItem
from tracker.models import DailyStepLog
from tracker.services import process_daily_steps
from tracker.constants import EXP_PER_STEP

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'One-time recovery: processes all unprocessed DailyStepLogs from past days'

    def handle(self, *args, **options):
        today = date.today()

        # ──────────────────────────────────────────
        # PHASE 1: AUDIT — Show what's missed
        # ──────────────────────────────────────────
        unprocessed_logs = DailyStepLog.objects.filter(
            is_processed=False,
            date__lt=today
        ).select_related('user').order_by('date')

        if not unprocessed_logs.exists():
            self.stdout.write(self.style.SUCCESS("✅ No unprocessed past logs found. Nothing to recover."))
            return

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("  📊 RECOVERY AUDIT — Missed Days Summary")
        self.stdout.write("=" * 60 + "\n")

        total_missed_steps = 0
        total_missed_exp = 0

        for log in unprocessed_logs:
            base_exp = math.floor(log.steps * EXP_PER_STEP)
            # Check for EXP boost from equipped items
            try:
                player = PlayerProfile.objects.get(user=log.user)
                exp_boost = 1.0
                equipped = InventoryItem.objects.filter(player=player, is_equipped=True).select_related('item')
                for inv in equipped:
                    if inv.item.exp_multiplier > 1.0:
                        exp_boost *= inv.item.exp_multiplier
                boosted_exp = math.floor(base_exp * exp_boost)
                boost_label = f" (×{exp_boost:.1f})" if exp_boost > 1.0 else ""
            except PlayerProfile.DoesNotExist:
                boosted_exp = base_exp
                boost_label = ""

            total_missed_steps += log.steps
            total_missed_exp += boosted_exp

            self.stdout.write(
                f"  📅 {log.date} | 👤 {log.user.username} | "
                f"👟 {log.steps:,} steps | ✨ +{boosted_exp:,} EXP{boost_label}"
            )

        self.stdout.write(f"\n  {'─' * 50}")
        self.stdout.write(f"  📦 Total missed: {total_missed_steps:,} steps → +{total_missed_exp:,} EXP")
        self.stdout.write(f"  📅 Days affected: {unprocessed_logs.count()}")

        # Show current dashboard state for each affected player
        affected_users = set(log.user_id for log in unprocessed_logs)
        self.stdout.write(f"\n  {'─' * 50}")
        self.stdout.write(f"  🎮 CURRENT DASHBOARD STATE:\n")
        for user_id in affected_users:
            try:
                player = PlayerProfile.objects.get(user_id=user_id)
                self.stdout.write(
                    f"  👤 {player.user.username} | Level {player.level} | "
                    f"EXP: {player.exp}/{player.exp_to_next_level}"
                )
            except PlayerProfile.DoesNotExist:
                pass

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("  ⚙️  PROCESSING MISSED DAYS...")
        self.stdout.write("=" * 60 + "\n")

        # ──────────────────────────────────────────
        # PHASE 2: PROCESS — Run the game engine
        # ──────────────────────────────────────────
        success_count = 0
        error_count = 0

        for log in unprocessed_logs:
            self.stdout.write(f"  Processing: {log.user.username} | {log.date} | {log.steps} steps")
            try:
                player = PlayerProfile.objects.get(user=log.user)
                old_level = player.level
                process_daily_steps(player, log)
                player.refresh_from_db()
                level_msg = f" 🎉 Level {old_level} → {player.level}!" if player.level > old_level else ""
                self.stdout.write(self.style.SUCCESS(
                    f"    ✅ Done! Level {player.level} | EXP: {player.exp}/{player.exp_to_next_level}{level_msg}"
                ))
                success_count += 1
            except PlayerProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"    ❌ No PlayerProfile for {log.user.username}. Skipping."))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ❌ Error: {str(e)}"))
                error_count += 1

        # ──────────────────────────────────────────
        # PHASE 3: SUMMARY — Show the result
        # ──────────────────────────────────────────
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(f"  🏁 RECOVERY COMPLETE")
        self.stdout.write(f"{'=' * 60}")
        self.stdout.write(f"  ✅ Processed: {success_count} | ❌ Errors: {error_count}\n")

        for user_id in affected_users:
            try:
                player = PlayerProfile.objects.get(user_id=user_id)
                self.stdout.write(
                    f"  👤 {player.user.username} | NOW Level {player.level} | "
                    f"EXP: {player.exp}/{player.exp_to_next_level}"
                )
            except PlayerProfile.DoesNotExist:
                pass

        if success_count > 0:
            self.stdout.write(self.style.SUCCESS(
                "\n  💡 Run 'process_stories' next to generate the AI stories for recovered days."
            ))
