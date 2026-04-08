import math
import random
import logging
from django.utils import timezone
from datetime import timedelta
from players.models import Item, InventoryItem
from .models import DailyStepLog, PendingStory
from .constants import *
from .utils import send_loot_email

# Setup logging for better debugging in cron jobs
logger = logging.getLogger(__name__)

def check_for_loot(player_profile, steps):
    """
    Per 5,000 steps → one loot roll with:
      50%    no loot
      26.5%  Common
      12.75% Rare
      6.84%  Epic
      3.91%  Legendary
    Multiple 5K thresholds = multiple independent rolls.
    """
    RARITY_TABLE = [
        (0.5000, None),                         # 50%    — no loot
        (0.7650, "Common"),                     # 26.5%  — cumulative 76.5%
        (0.8925, "Rare"),                       # 12.75% — cumulative 89.25%
        (0.9609, "Epic"),                       # 6.84%  — cumulative 96.09%
        (1.0000, "Legendary"),                  # 3.91%  — cumulative 100%
    ]
    num_rolls = steps // 5000
    best_item = None  # Track the best item found (for the story)
    for _ in range(num_rolls):
        roll = random.random()
        chosen_rarity = None
        for threshold, rarity in RARITY_TABLE:
            if roll < threshold:
                chosen_rarity = rarity
                break
        if chosen_rarity is None:
            continue                             # No loot this roll
        possible_items = list(Item.objects.filter(rarity=chosen_rarity))
        if possible_items:
            found_item = random.choice(possible_items)
            # Check if player already has this item
            inv_item, created = InventoryItem.objects.get_or_create(
                player=player_profile, 
                item=found_item,
                defaults={'quantity': 1}
            )
            if not created:
                inv_item.quantity += 1
                inv_item.save()
            # prioritize higher rarity if multiple items drop (best item for the story mention)
            if best_item is None:
                best_item = found_item
            else:
                rarity_rank = {"Common": 1, "Rare": 2, "Epic": 3, "Legendary": 4}
                if rarity_rank.get(found_item.rarity, 0) > rarity_rank.get(best_item.rarity, 0):
                    best_item = found_item
            if found_item:
                # for sending an email
                if found_item.rarity in ["Epic", "Legendary"] and player_profile.user.email:
                    send_loot_email(
                        user_email=player_profile.user.email,
                        player_name=player_profile.user.username,
                        item_name=found_item.name,
                        rarity=found_item.rarity,
                        template_id=3                       # Brevo Template ID
                    )

    return best_item

def calculate_required_exp(current_level):
    return math.floor(BASE_XP_REQ * (current_level ** LEVEL_EXPONENT))

def process_daily_steps(player_profile, step_log):
    """
    The core engine: Converts steps to EXP, handles leveling, 
    unlocks regions, and triggers AI storytelling.
    """
    if step_log.is_processed:                       # 1. Safety Check: Don't process the same log twice
        logger.warning(f"Attempted to re-process log {step_log.id}")
        return False
    # 2. EXP Calculation
    # Find any equipped items that give an EXP boost
    exp_boost = 1.0
    equipped_items = player_profile.inventory.filter(is_equipped=True)
    for item in equipped_items:
        if item.item.exp_multiplier > 1.0:
            # Example: if you have a 1.2x item and a 1.1x item, it stacks!
            exp_boost *= item.item.exp_multiplier
    # Apply the boost to today's steps!
    base_exp = math.floor(step_log.steps * EXP_PER_STEP)
    total_exp_gained = math.floor(base_exp * exp_boost)
    player_profile.exp += total_exp_gained
    logger.info(f"⚔️ {player_profile.user.username}: +{total_exp_gained} EXP from {step_log.steps} steps.")
    # List to collect levels reached for scheduled storytelling
    levels_gained = []
    # 3. Processing Levels & Region Discoveries
    any_level_up_occurred = False                  
    while True:
        req_exp = calculate_required_exp(player_profile.level)
        if player_profile.exp >= req_exp:
            # Level Up
            player_profile.exp -= req_exp
            player_profile.level += 1
            player_profile.base_hp += 10
            player_profile.base_mana += 2
            any_level_up_occurred = True
            # Check for New Regions
            if player_profile.level in WORLD_REGIONS:
                new_zone = WORLD_REGIONS[player_profile.level]
                player_profile.current_location = new_zone["location"]
                player_profile.world_region = new_zone["region"]
                logger.info(f"🗺️ DISCOVERY: Reached {player_profile.current_location}")
            # Store this milestone level for the queue
            levels_gained.append(player_profile.level)
            # Save state before calling AI
            player_profile.save()
            print(f"--- ✨ Level Up! Now Level {player_profile.level}. Queuing Chapter... ---")
        else:
            break
    # Save to DB before creating PendingStory
    player_profile.refresh_from_db()

    # 4. Check for Loot
    found_item = check_for_loot(player_profile, step_log.steps)
    found_item_name = found_item.name if found_item else None
    story_date = str(step_log.date)  # Serialize date
    # 5. Scheduling the Story Drip-Feed
    if any_level_up_occurred:
        # Loop through each level gained & schedule a task
        for index, lv in enumerate(levels_gained):
            delay_minutes = index * 15                  # 15 minutes delay per level
            run_at = timezone.now() + timedelta(minutes=delay_minutes)
            PendingStory.objects.create(
                player=player_profile,
                steps=step_log.steps,
                exp_gained=total_exp_gained,
                leveled_up=True,
                target_level=lv,
                story_date=story_date,
                found_item_name=found_item_name,
                scheduled_time=run_at
            )
            logger.info(f"⏲️ Saved PendingStory for Level {lv} scheduled at {run_at}.")
    # 6. Daily Summary (If player didn't level up at all)
    else:
        logger.info("📜 Saving PendingStory for daily adventure summary (no level up).")
        run_at = timezone.now()
        PendingStory.objects.create(
            player=player_profile,
            steps=step_log.steps,
            exp_gained=total_exp_gained,
            leveled_up=False,
            target_level=None,
            story_date=story_date,
            found_item_name=found_item_name,
            scheduled_time=run_at
        )
    player_profile.save()
    step_log.is_processed = True
    step_log.save()
    
    return True
