import os
import django
from django.conf import settings

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isekai_tracker.settings')
django.setup()

from tracker.utils import send_loot_email

def test_loot_notification(email):
    print(f"--- Sending Test Loot Email to {email} ---")
    try:
        send_loot_email(
            user_email=email,
            player_name="TestHero",
            item_name="Crown of the Void",
            rarity="Legendary",
            template_id=3
        )
        print("Success: Notification sent!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_loot_notification(sys.argv[1])
    else:
        print("Usage: python test_loot_email.py <your-email@example.com>")
