from django.contrib import admin
from .models import PlayerProfile, Item, InventoryItem

# Register your models here.
admin.site.register(PlayerProfile)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'rarity', 'hp_bonus', 'mana_bonus', 'exp_multiplier')
    list_filter = ('item_type', 'rarity')
    search_fields = ('name',)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('player', 'get_item_name', 'is_equipped', 'acquired_at')
    list_filter = ('is_equipped', 'item__rarity', 'item__item_type')
    search_fields = ('player__user__username', 'item__name')
    # Helper to show the item name in the list view
    def get_item_name(self, obj):
        return obj.item.name
    get_item_name.short_description = 'Item'
