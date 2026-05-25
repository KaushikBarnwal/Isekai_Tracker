from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import PlayerProfile, InventoryItem

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'players/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    from datetime import date
    from tracker.models import DailyStepLog
    
    player, _ = PlayerProfile.objects.get_or_create(user=request.user)
    equipped_list = InventoryItem.objects.filter(
        player=player, 
        is_equipped=True
    ).select_related('item')
    equipment = {
        'weapon': equipped_list.filter(item__item_type='WEAPON').first(),
        'armor': equipped_list.filter(item__item_type='ARMOR').first(),
        'artifact': equipped_list.filter(item__item_type='ARTIFACT').first(),
        'consumable': equipped_list.filter(item__item_type='CONSUMABLE').first(),
    }
    today_log = DailyStepLog.objects.filter(user=request.user, date=date.today()).first()
    today_steps = today_log.steps if today_log else 0
    step_goal = 10000
    step_progress_percentage = min((today_steps / step_goal) * 100, 100)
    context = {
        'player': player,
        'equipment': equipment,
        'today_steps': today_steps,
        'step_goal': step_goal,
        'step_progress_percentage': step_progress_percentage,
    }
    return render(request, 'players/dashboard.html', context)

@login_required
def inventory_page(request):
    player, _ = PlayerProfile.objects.get_or_create(user=request.user)
    # Fetch all items owned by the player, ordered by newest first, optimized with select_related
    inventory = InventoryItem.objects.filter(player=player).select_related('item').order_by('-acquired_at')
    context = {
        'player': player,
        'inventory': inventory,
    }
    return render(request, 'players/inventory.html', context)

@login_required
def toggle_equip(request, inventory_id):
    if request.method == 'POST':
        player, _ = PlayerProfile.objects.get_or_create(user=request.user)
        # Ensure the user actually owns this specific item
        inv_item = get_object_or_404(InventoryItem, id=inventory_id, player=player)
        if inv_item.is_equipped:
            inv_item.is_equipped = False                    # Unequip the item
            inv_item.save()
        else:
            # Equip the new item
            # Find if they are already wearing an item of this type (like another weapon)
            currently_equipped = InventoryItem.objects.filter(
                player=player, 
                is_equipped=True, 
                item__item_type=inv_item.item.item_type
            )
            for old_item in currently_equipped:             # Unequip the old item(s)
                old_item.is_equipped = False
                old_item.save()
            inv_item.is_equipped = True                     # Equip the new item 
            inv_item.save()
        player.save()                                       # Save the player's new stats
    return redirect('inventory')                            # Refresh the page so the user sees the changes