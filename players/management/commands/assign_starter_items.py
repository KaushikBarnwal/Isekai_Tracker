from django.core.management.base import BaseCommand
from players.models import PlayerProfile, Item, InventoryItem

STARTER_ITEM_NAMES = [
    # Weapons
    "Wooden Bokken",
    "Rusty Dagger",
    # Armor
    "Traveler's Cloak",
    "Rough Leather Boots",
    # Consumables
    "Minor Health Potion",
    "Small Mana Potion",
]


class Command(BaseCommand):
    help = "Assigns a set of Common starter items to every existing PlayerProfile"

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching starter items from the armory...")

        # Resolve all starter items up front so we can fail fast if any are missing
        starter_items = []
        missing = []
        for name in STARTER_ITEM_NAMES:
            try:
                starter_items.append(Item.objects.get(name=name))
            except Item.DoesNotExist:
                missing.append(name)

        if missing:
            self.stdout.write(
                self.style.ERROR(
                    f"The following starter items were not found in the database: "
                    f"{', '.join(missing)}. "
                    f"Run 'python manage.py seed_items' first, then retry."
                )
            )
            return

        players = PlayerProfile.objects.select_related("user").all()
        if not players.exists():
            self.stdout.write(self.style.WARNING("No PlayerProfile records found. Nothing to do."))
            return

        total_assigned = 0
        total_skipped = 0

        for player in players:
            self.stdout.write(f"\nProcessing player: {player.user.username}")
            for item in starter_items:
                inv_item, created = InventoryItem.objects.get_or_create(
                    player=player,
                    item=item,
                    defaults={"quantity": 1, "is_equipped": False},
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [+] Assigned '{item.name}' ({item.rarity}) to {player.user.username}"
                        )
                    )
                    total_assigned += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  [~] '{item.name}' already in {player.user.username}'s inventory — skipped"
                        )
                    )
                    total_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n--- Done! {total_assigned} item(s) assigned, "
                f"{total_skipped} already existed and were skipped. ---"
            )
        )
