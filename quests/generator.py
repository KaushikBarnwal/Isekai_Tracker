# import fal_client
import re # For robust text parsing
import random
from django.conf import settings
# from google import genai
# from google.genai import types
from groq import Groq
# from openai import OpenAI
from players.models import PlayerProfile, InventoryItem
from tracker.constants import *
from .models import DailyStory

# GEMINI_CLIENT = genai.Client(api_key=settings.GEMINI_API_KEY)
# GEMINI_IMAGE_CLIENT = genai.Client(api_key=settings.GEMINI_IMAGE_API_KEY)
GROQ_CLIENT = Groq(api_key=settings.GROQ_API_KEY)

# from openai import OpenAI
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

    # 1: Text Generation (Groq / Llama 3)
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
    
    IMPORTANT: Provide the response in this EXACT format:
    STORY: [The story content]
    SUMMARY: [The summary content]
    ACTION: [The action phrase]
    """
    
    print("--- DEBUG: Calling Groq API ---")
    # Using Llama 3.3 70B for high quality, or Llama 3 8B for extreme speed
    try:
        chat_completion = GROQ_CLIENT.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative writer for an Isekai adventure game."
                },
                {
                    "role": "user",
                    "content": narrative_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )
        raw_text = chat_completion.choices[0].message.content
        print(f"--- DEBUG: Groq Response: {raw_text[:50]}... ---")
    except Exception as e:
        print(f"--- ERROR: Groq API Call failed: {e} ---")
        raw_text = f"STORY: The hero {player.user.username} pushed forward into the unknown. SUMMARY: The journey continues. ACTION: walking through the woods"

    # Text Parsing (Upgraded to Regex to prevent crashes)
    try:
        story_match = re.search(r"STORY:(.*?)SUMMARY:", raw_text, re.DOTALL | re.IGNORECASE)
        summary_match = re.search(r"SUMMARY:(.*?)ACTION:", raw_text, re.DOTALL | re.IGNORECASE)
        action_match = re.search(r"ACTION:(.*)", raw_text, re.DOTALL | re.IGNORECASE)
        
        story_content = story_match.group(1).replace('#', '').replace('*', '').strip() if story_match else "The hero pushed forward."
        summary_content = summary_match.group(1).replace('#', '').replace('*', '').strip() if summary_match else "The journey continues."
        current_action = action_match.group(1).replace('#', '').replace('*', '').strip() if action_match else "exploring the world"
        
        # Fallback if story_match failed but raw_text exists
        if not story_match and len(raw_text) > 50:
             story_content = raw_text[:500] 
    except Exception as e:
        print(f"--- ERROR: Parsing failed: {e} ---")
        story_content = f"The hero {player.user.username} pushed forward into the unknown."
        summary_content = "The journey continues deeper into the world."
        current_action = "walking through a mysterious landscape"

    # 2: Image Generation (Hugging Face -> Cloudinary)
    import requests
    import cloudinary.uploader
    
    dna_string = f"{player.visual_description}, wearing {gear_context}"
    prompt_text = f"{dna_string}, {current_action}, {player.current_location} background, anime style"
    
    print("--- DEBUG: Calling Hugging Face API ---")
    hf_token = settings.HUGGINGFACE_API_KEY
    # Using FLUX.1-schnell for fast, high-quality generation
    api_url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt_text}
    
    generated_image_url = ""
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            print("--- DEBUG: Hugging Face Success. Uploading to Cloudinary ---")
            image_bytes = response.content
            # Upload to cloudinary
            upload_result = cloudinary.uploader.upload(
                image_bytes, 
                folder="isekai_tracker/stories",
                resource_type="image"
            )
            generated_image_url = upload_result.get("secure_url", "")
            print(f"--- DEBUG: Cloudinary URL generated: {generated_image_url} ---")
        else:
            print(f"--- ERROR: Hugging Face failed: {response.status_code} {response.text} ---")
    except Exception as e:
        print(f"--- ERROR: Image pipeline failed: {e} ---")

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
