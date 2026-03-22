# import fal_client
import re # For robust text parsing
import random
from django.conf import settings
from google import genai
from google.genai import types

# from openai import OpenAI
from players.models import PlayerProfile, InventoryItem
from tracker.constants import *
from .models import DailyStory

GEMINI_CLIENT = genai.Client(api_key=settings.GEMINI_API_KEY)
GEMINI_IMAGE_CLIENT = genai.Client(api_key=settings.GEMINI_IMAGE_API_KEY)
# SF_CLIENT = OpenAI(
#     api_key = settings.SILICONFLOW_API_KEY,
#     base_url = "https://api.siliconflow.cn/v1"
# )

# Added target_level to ensure delayed tasks write for the correct milestone
def generate_isekai_chapter(player_id, steps, exp_gained, leveled_up, target_level=None, found_item=None, story_date=None):
    print(f"--- DEBUG: Starting Story Gen for Player {player_id} ---")
    player = PlayerProfile.objects.get(id=player_id)
    # Fetch Equipped Gear
    equipped_items = InventoryItem.objects.filter(player=player, is_equipped=True).select_related('item')
    gear_names = [inv.item.name for inv in equipped_items]
    gear_context = ", ".join(gear_names) if gear_names else "basic travel rags and no weapons"
    # If a specific level is requested by the queue, use it. Otherwise, use current level.
    current_story_level = target_level if target_level is not None else player.level
    last_story = DailyStory.objects.filter(player=player).order_by('-date').first()
    previous_memory = last_story.memory_summary if last_story else "The hero awakens in a new world with no memory."
    item_context = f"During the journey, the hero discovered a {found_item.name}!" if found_item else ""
    story_length = "6-sentence epic chapter" if (current_story_level % 10 == 0) else "3-sentence immersive narrative chapter"
    if random.random() < 0.30: 
        # 30% Chance: Combat Day
        enemy_list = REGION_ENEMIES.get(player.world_region, ["Wandering Beasts"])
        chosen_enemy = random.choice(enemy_list) # Pick ONE specific enemy for the AI to focus on
        day_vibe = f"Combat Encounter: The hero is ambushed by or battles a {chosen_enemy}."
    else:
        # 70% Chance: Peaceful Day
        day_vibe = "Peaceful Exploration: The hero travels safely, admires the scenery, camps, or discovers a peaceful landmark. NO COMBAT."

    # 1: Text Generation (Gemini)
    narrative_prompt = f"""
    {item_context}
    System: You are an Isekai Light Novel narrator.
    Character DNA: {player.visual_description}
    Current Gear: {gear_context}
    World State: Currently in {player.current_location} ({player.world_region}).
    Today's Event: {day_vibe}
    Previous Context: {previous_memory}
    Today's Data: {player.user.username} walked {steps} steps and gained {exp_gained} EXP.
    Level Progress: Now Level {current_story_level}. Leveled Up: {leveled_up}.
    Task:
    1. STORY: Write a {story_length} focusing on Today's Event. MENTION the hero using or wearing their {gear_context} naturally in the action.
    2. SUMMARY: A 1-sentence summary of the plot for tomorrow's memory.
    3. ACTION: A short 3-5 word phrase describing ONLY the primary physical action the character is doing right now (e.g., 'swinging a sword', 'running through the forest', 'resting by a fire'). Do not describe their appearance or gear.
    """
    print("--- DEBUG: Calling Gemini API ---")
    response = GEMINI_CLIENT.models.generate_content(
        model = "gemini-2.0-flash",
        contents = narrative_prompt
    )
    print(f"--- DEBUG: Gemini Response: {response.text[:50]}... ---")

    # Text Parsing (Upgraded to Regex to prevent crashes)
    raw_text = response.text
    try:
        story_match = re.search(r"STORY:(.*?)SUMMARY:", raw_text, re.DOTALL)
        summary_match = re.search(r"SUMMARY:(.*?)ACTION:", raw_text, re.DOTALL)
        action_match = re.search(r"ACTION:(.*)", raw_text, re.DOTALL)
        
        story_content = story_match.group(1).replace('#', '').replace('*', '').strip() if story_match else f"The hero {player.user.username} pushed forward into the unknown."
        summary_content = summary_match.group(1).replace('#', '').replace('*', '').strip() if summary_match else "The journey continues deeper into the world."
        current_action = action_match.group(1).replace('#', '').replace('*', '').strip() if action_match else "walking through a mysterious landscape"
    except Exception as e:
        print(f"--- ERROR: Parsing failed: {e} ---")
        story_content = f"The hero {player.user.username} pushed forward into the unknown."
        summary_content = "The journey continues deeper into the world."
        current_action = "walking through a mysterious landscape"

    # 2: Image Generation (Pollinations.ai with Same Face Strategy)
    import urllib.parse
    dna_string = f"{player.visual_description}, wearing {gear_context}"
    # Combine DNA and Action
    prompt_text = f"{dna_string}, {current_action}, {player.current_location} background, anime style"
    encoded_prompt = urllib.parse.quote(prompt_text)
    
    fixed_seed = player.ai_seed
    generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={fixed_seed}&model=flux&width=1024&height=1024"
    print(f"--- DEBUG: Pollinations URL generated ---")

    # 3: Saving to Database
    create_kwargs = dict(
        player = player,
        content = story_content,
        memory_summary = summary_content,
        image_url = generated_image_url,
        level_at_time = current_story_level,
        world_region = player.world_region,
        location_name = player.current_location,
        steps_taken = steps,
        exp_gained = exp_gained,
        found_item_name = found_item.name if found_item else None,
    )
    if story_date:
        create_kwargs['date'] = story_date
    new_entry = DailyStory.objects.create(**create_kwargs)
    return new_entry