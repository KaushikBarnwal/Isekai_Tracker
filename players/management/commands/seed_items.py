from django.core.management.base import BaseCommand
from players.models import Item

class Command(BaseCommand):
    help = 'Seeds the database with the official Isekai Loot Table'

    def handle(self, *args, **kwargs):
        self.stdout.write("Forging items in the database...")

        loot_table = [
            # 🟩 COMMON (15 Items)
            {"name": "Wooden Bokken", "item_type": "WEAPON", "rarity": "Common", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "A sturdy practice sword from the village."},
            {"name": "Apprentice Wand", "item_type": "WEAPON", "rarity": "Common", "hp_bonus": 0, "mana_bonus": 5, "exp_multiplier": 1.0, "description": "A simple oak stick that channels a tiny spark."},
            {"name": "Rusty Dagger", "item_type": "WEAPON", "rarity": "Common", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Better than fighting with bare hands."},
            {"name": "Traveler's Cloak", "item_type": "ARMOR", "rarity": "Common", "hp_bonus": 5, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Keeps the rain off, but won't stop a blade."},
            {"name": "Straw Hat", "item_type": "ARMOR", "rarity": "Common", "hp_bonus": 2, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Protects you from the sun during long walks."},
            {"name": "Rough Leather Boots", "item_type": "ARMOR", "rarity": "Common", "hp_bonus": 3, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Sturdy enough for the dirt paths of the starting village."},
            {"name": "Minor Health Potion", "item_type": "CONSUMABLE", "rarity": "Common", "hp_bonus": 20, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "A slightly bitter red liquid that closes small wounds."},
            {"name": "Stale Bread", "item_type": "CONSUMABLE", "rarity": "Common", "hp_bonus": 5, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Hard as a rock, but provides a small burst of energy."},
            {"name": "Small Mana Potion", "item_type": "CONSUMABLE", "rarity": "Common", "hp_bonus": 0, "mana_bonus": 10, "exp_multiplier": 1.0, "description": "A fizzy blue drink that tastes like blueberries."},
            {"name": "Copper Ring", "item_type": "ARTIFACT", "rarity": "Common", "hp_bonus": 0, "mana_bonus": 2, "exp_multiplier": 1.0, "description": "A simple band that hums with a faint energy."},
            {"name": "Faded Map", "item_type": "ARTIFACT", "rarity": "Common", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.02, "description": "An old map of the kingdom. Grants 2% bonus EXP."},
            {"name": "Lucky Pebble", "item_type": "ARTIFACT", "rarity": "Common", "hp_bonus": 1, "mana_bonus": 1, "exp_multiplier": 1.0, "description": "It feels warm to the touch. Maybe it really is lucky."},
            {"name": "Iron Bracer", "item_type": "ACCESSORY", "rarity": "Common", "hp_bonus": 4, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "A heavy metal band for your forearm."},
            {"name": "Simple Bandana", "item_type": "ACCESSORY", "rarity": "Common", "hp_bonus": 0, "mana_bonus": 3, "exp_multiplier": 1.0, "description": "Helps you focus your thoughts."},
            {"name": "Linen Belt", "item_type": "ACCESSORY", "rarity": "Common", "hp_bonus": 2, "mana_bonus": 2, "exp_multiplier": 1.0, "description": "A plain belt with many small pockets."},

            # 🟦 RARE (15 Items)
            {"name": "Iron-Forged Broadsword", "item_type": "WEAPON", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.05, "description": "A reliable blade used by town guards. Grants 5% bonus EXP."},
            {"name": "Spellbound Staff", "item_type": "WEAPON", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 25, "exp_multiplier": 1.0, "description": "Encased in crystal, this staff glows when magic is near."},
            {"name": "Silver Rapier", "item_type": "WEAPON", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.07, "description": "Swift and elegant. Grants 7% bonus EXP."},
            {"name": "Wolf-Pelt Tunic", "item_type": "ARMOR", "rarity": "Rare", "hp_bonus": 15, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Warm and thick, smells slightly of wet dog."},
            {"name": "Steel Bracers", "item_type": "ARMOR", "rarity": "Rare", "hp_bonus": 10, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Solid protection for a wandering warrior."},
            {"name": "Reinforced Gambeson", "item_type": "ARMOR", "rarity": "Rare", "hp_bonus": 20, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Layers of linen and wool designed to absorb impact."},
            {"name": "Elixir of Speed", "item_type": "CONSUMABLE", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.10, "description": "Increases your pace. Grants 10% bonus EXP for the next walk."},
            {"name": "Greater Health Potion", "item_type": "CONSUMABLE", "rarity": "Rare", "hp_bonus": 50, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "A thick crimson brew that repairs deep gashes."},
            {"name": "Potion of Mana Surge", "item_type": "CONSUMABLE", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 40, "exp_multiplier": 1.0, "description": "A glowing liquid that smells of ozone."},
            {"name": "Mana Crystal Shard", "item_type": "ARTIFACT", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 10, "exp_multiplier": 1.0, "description": "Pulses with a faint blue light."},
            {"name": "Ancient Coin", "item_type": "ARTIFACT", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.08, "description": "Currency from a fallen empire. Grants 8% bonus EXP."},
            {"name": "Surveyor's Lens", "item_type": "ARTIFACT", "rarity": "Rare", "hp_bonus": 5, "mana_bonus": 5, "exp_multiplier": 1.0, "description": "Reveals hidden paths and secrets."},
            {"name": "Emerald Pendant", "item_type": "ACCESSORY", "rarity": "Rare", "hp_bonus": 12, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "A beautiful gem that seems to radiate health."},
            {"name": "Cloak of Shadows", "item_type": "ACCESSORY", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 15, "exp_multiplier": 1.0, "description": "Makes the wearer slightly harder to spot in the dark."},
            {"name": "Leather Scabbard", "item_type": "ACCESSORY", "rarity": "Rare", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.04, "description": "A masterfully crafted sheath. Grants 4% bonus EXP."},

            # 🟪 EPIC (15 Items)
            {"name": "Blade of the Whispering Woods", "item_type": "WEAPON", "rarity": "Epic", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.15, "description": "A sword forged from ancient, glowing wood. Grants 15% bonus EXP."},
            {"name": "Void-Touched Scythe", "item_type": "WEAPON", "rarity": "Epic", "hp_bonus": 0, "mana_bonus": 50, "exp_multiplier": 1.0, "description": "Harvests the essence of fallen foes."},
            {"name": "Storm-Caller Bow", "item_type": "WEAPON", "rarity": "Epic", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.20, "description": "Arrows fired from this bow crackle with lightning. Grants 20% bonus EXP."},
            {"name": "Mythril Chainmail", "item_type": "ARMOR", "rarity": "Epic", "hp_bonus": 50, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Incredibly light, yet stronger than steel."},
            {"name": "Dragon-Scale Greaves", "item_type": "ARMOR", "rarity": "Epic", "hp_bonus": 40, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Leg armor forged from the scales of a young drake."},
            {"name": "Phoenix Feather Tunic", "item_type": "ARMOR", "rarity": "Epic", "hp_bonus": 30, "mana_bonus": 20, "exp_multiplier": 1.0, "description": "Radiates a constant, comforting warmth."},
            {"name": "Ambrosia", "item_type": "CONSUMABLE", "rarity": "Epic", "hp_bonus": 150, "mana_bonus": 50, "exp_multiplier": 1.0, "description": "Food of the ancients. Fully restores vitality."},
            {"name": "Draught of Giant Strength", "item_type": "CONSUMABLE", "rarity": "Epic", "hp_bonus": 100, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Your muscles bulge with unnatural power."},
            {"name": "Forbidden Scroll", "item_type": "CONSUMABLE", "rarity": "Epic", "hp_bonus": 0, "mana_bonus": 100, "exp_multiplier": 1.0, "description": "A dark text that unlocks deep magical reserves."},
            {"name": "Ring of the Wind Walker", "item_type": "ARTIFACT", "rarity": "Epic", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.25, "description": "Makes the wearer's footsteps silent and swift. Grants 25% bonus EXP."},
            {"name": "Chronos Hourglass", "item_type": "ARTIFACT", "rarity": "Epic", "hp_bonus": 0, "mana_bonus": 30, "exp_multiplier": 1.0, "description": "Allows the wearer to sense the flow of time."},
            {"name": "Eye of the Beholder", "item_type": "ARTIFACT", "rarity": "Epic", "hp_bonus": 10, "mana_bonus": 40, "exp_multiplier": 1.0, "description": "A floating orb that grants true sight."},
            {"name": "Celestial Veil", "item_type": "ACCESSORY", "rarity": "Epic", "hp_bonus": 0, "mana_bonus": 60, "exp_multiplier": 1.0, "description": "A shimmering cloth that tastes like starlight."},
            {"name": "Navigator's Compass", "item_type": "ACCESSORY", "rarity": "Epic", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.30, "description": "Always points toward destiny. Grants 30% bonus EXP."},
            {"name": "Spirit Amulet", "item_type": "ACCESSORY", "rarity": "Epic", "hp_bonus": 25, "mana_bonus": 25, "exp_multiplier": 1.0, "description": "Connects your soul to the ethereal plane."},

            # 🟧 LEGENDARY (15 Items)
            {"name": "Excalibur of the Sun", "item_type": "WEAPON", "rarity": "Legendary", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 1.50, "description": "A blade of pure, concentrated light. Blinds enemies on sight. Grants 50% bonus EXP."},
            {"name": "World-Eater's Axe", "item_type": "WEAPON", "rarity": "Legendary", "hp_bonus": 100, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "An axe that trembles with the hunger of a thousand years."},
            {"name": "God-Slayer's Spear", "item_type": "WEAPON", "rarity": "Legendary", "hp_bonus": 0, "mana_bonus": 200, "exp_multiplier": 1.0, "description": "A weapon designed to pierce the heavens themselves."},
            {"name": "Aegis of the Iron Golem", "item_type": "ARMOR", "rarity": "Legendary", "hp_bonus": 200, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Armor so heavy that only a true hero can move while wearing it."},
            {"name": "Armor of the Eternal King", "item_type": "ARMOR", "rarity": "Legendary", "hp_bonus": 150, "mana_bonus": 100, "exp_multiplier": 1.0, "description": "The regalia of a sovereign who ruled for an eternity."},
            {"name": "Robes of the Archmagi", "item_type": "ARMOR", "rarity": "Legendary", "hp_bonus": 50, "mana_bonus": 300, "exp_multiplier": 1.0, "description": "Woven from distilled mana and dragon silk."},
            {"name": "Nectar of the Gods", "item_type": "CONSUMABLE", "rarity": "Legendary", "hp_bonus": 500, "mana_bonus": 500, "exp_multiplier": 1.0, "description": "A single drop grants life eternal and infinite wisdom."},
            {"name": "Panacea of Life", "item_type": "CONSUMABLE", "rarity": "Legendary", "hp_bonus": 1000, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "Cures all ailments and restores every drop of vitality."},
            {"name": "Scroll of Absolute Power", "item_type": "CONSUMABLE", "rarity": "Legendary", "hp_bonus": 0, "mana_bonus": 1000, "exp_multiplier": 1.0, "description": "The words on this scroll reshape reality itself."},
            {"name": "Tear of the Goddess", "item_type": "ARTIFACT", "rarity": "Legendary", "hp_bonus": 0, "mana_bonus": 500, "exp_multiplier": 1.0, "description": "A mythical gem said to grant infinite magical potential."},
            {"name": "Heart of the Star", "item_type": "ARTIFACT", "rarity": "Legendary", "hp_bonus": 250, "mana_bonus": 250, "exp_multiplier": 1.0, "description": "The core of a dying sun, pulsing with raw creation."},
            {"name": "Eye of Fate", "item_type": "ARTIFACT", "rarity": "Legendary", "hp_bonus": 0, "mana_bonus": 0, "exp_multiplier": 2.00, "description": "Allows the wearer to see every possible future. Grants 100% bonus EXP."},
            {"name": "Key to the Multiverse", "item_type": "ARTIFACT", "rarity": "Legendary", "hp_bonus": 100, "mana_bonus": 100, "exp_multiplier": 1.20, "description": "A key that unlocks doors to other realities."},
            {"name": "Cloak of Immortality", "item_type": "ACCESSORY", "rarity": "Legendary", "hp_bonus": 300, "mana_bonus": 0, "exp_multiplier": 1.0, "description": "A cape that makes the wearer impervious to the passage of time."},
            {"name": "Crown of the Void", "item_type": "ACCESSORY", "rarity": "Legendary", "hp_bonus": 0, "mana_bonus": 600, "exp_multiplier": 1.0, "description": "A crown made of pure nothingness. Commands the shadows."},
        ]

        items_created = 0
        for data in loot_table:
            item, created = Item.objects.get_or_create(
                name=data['name'],
                defaults={
                    'item_type': data['item_type'],
                    'rarity': data['rarity'],
                    'hp_bonus': data['hp_bonus'],
                    'mana_bonus': data['mana_bonus'],
                    'exp_multiplier': data['exp_multiplier'],
                    'description': data['description'],
                }
            )
            if created:
                items_created += 1
                self.stdout.write(self.style.SUCCESS(f"Forged: {item.name} [{item.rarity}]"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {item.name}"))

        self.stdout.write(self.style.SUCCESS(f"--- Armory Complete! {items_created} new items added. ---"))
