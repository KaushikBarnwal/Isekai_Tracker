# import math
from django.db import models
from django.contrib.auth.models import User
from django.contrib import messages

# Create your models here.
class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Stats
    level = models.PositiveIntegerField(default=1)
    exp = models.PositiveIntegerField(default=0)
    base_hp = models.PositiveIntegerField(default=100)
    base_mana = models.PositiveIntegerField(default=20)
    character_class = models.CharField(max_length=100, default="Novice")
    # OAuth Fields
    google_access_token = models.TextField(null=True, blank=True)
    google_refresh_token = models.TextField(null=True, blank=True)
    google_token_uri = models.URLField(null=True, blank=True)
    google_client_id = models.TextField(null=True, blank=True)
    google_client_secret = models.TextField(null=True, blank=True)
    # Narrative & Visual DNA
    current_location = models.CharField(
        max_length=255, 
        default="The Humble Village of Starting"
    )
    visual_description = models.TextField(
        default="Male Isekai protagonist, messy black hair, sharp blue eyes, athletic build"
    )
    world_region = models.CharField(
        max_length=100,
        default="Greenleaf Kingdom"
    )
    ai_seed = models.IntegerField(default=42)

    def __str__(self):
        return f"{self.user.username} - Level {self.level} {self.character_class} ({self.current_location}, {self.world_region})"

    @property
    def hp(self):
        bonus = sum(inv.item.hp_bonus for inv in self.inventory.all() if inv.is_equipped)
        return self.base_hp + bonus

    @property
    def mana(self):
        bonus = sum(inv.item.mana_bonus for inv in self.inventory.all() if inv.is_equipped)
        return self.base_mana + bonus

    @property
    def exp_to_next_level(self):
        import math
        from tracker.constants import BASE_XP_REQ, LEVEL_EXPONENT
        return math.floor(BASE_XP_REQ * (self.level ** LEVEL_EXPONENT))

    @property
    def exp_progress_percentage(self):
        req = self.exp_to_next_level
        if req == 0: return 100
        perc = (self.exp / req) * 100
        return min(max(perc, 0), 100)

class Item(models.Model):
    ITEM_TYPES = [
        ('WEAPON', 'Weapon'),
        ('ARMOR', 'Armor'),
        ('CONSUMABLE', 'Consumable'),
        ('ARTIFACT', 'Artifact'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    rarity = models.CharField(max_length=20, default="Common")
    # Stat Boosts
    hp_bonus = models.IntegerField(default=0)
    mana_bonus = models.IntegerField(default=0)
    exp_multiplier = models.FloatField(default=1.0)
    image_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.rarity})"

class InventoryItem(models.Model):
    player = models.ForeignKey('PlayerProfile', on_delete=models.CASCADE, related_name="inventory")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_equipped = models.BooleanField(default=False)
    acquired_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username}'s {self.item.name} (x{self.quantity})"