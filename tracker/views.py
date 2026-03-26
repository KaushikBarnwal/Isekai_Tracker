from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from players.models import PlayerProfile
from .models import DailyStepLog
from quests.models import DailyStory
from .services import process_daily_steps
from .fit_service import FitService

def google_fit_login(request):
    callback_url = request.build_absolute_uri(reverse('google_fit_callback'))
    flow = FitService.get_flow(redirect_uri=callback_url)
    authorization_url, state = flow.authorization_url(prompt='consent')
    request.session['oauth_state'] = state
    request.session['code_verifier'] = flow.code_verifier
    return redirect(authorization_url)

@login_required
def google_fit_callback(request):
    state = request.session.pop('oauth_state', None)
    code_verifier = request.session.pop('code_verifier', None)
    if not state or state != request.GET.get('state'):
        return HttpResponse("Invalid state parameter", status=400)
    callback_url = request.build_absolute_uri(reverse('google_fit_callback'))
    flow = FitService.get_flow(redirect_uri=callback_url)
    if code_verifier:
        flow.code_verifier = code_verifier
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials                     # Store credentials in the Database instead of session
    player = PlayerProfile.objects.get(user=request.user)
    player.google_access_token = credentials.token
    player.google_refresh_token = credentials.refresh_token
    player.google_token_uri = credentials.token_uri
    player.google_client_id = credentials.client_id
    player.google_client_secret = credentials.client_secret
    player.save()
    messages.success(request, "Google Fit connected successfully! 🎉 Your hero is now synced to the real world. 🌍")
    return redirect('dashboard')

def test_isekai_trigger(request, player_id, steps):
    player = get_object_or_404(PlayerProfile, id=player_id)
    # Check for today's log based ONLY on user and date
    # Then update the steps if it's not processed yet
    step_log, created = DailyStepLog.objects.get_or_create(
        user=player.user,
        date=date.today(),                  # Specifically target today
        defaults={'steps': steps, 'is_processed': False}
    )
    if not created:
        if step_log.is_processed:
            return JsonResponse({"status": "Error", "message": "Today's journey is already complete!"})
        # If it's not processed, update the steps for the test
        step_log.steps = steps
        step_log.save()
    # Fire the Engine
    success = process_daily_steps(player, step_log)
    if success:
        return JsonResponse({
            "status": "Success",
            "message": f"Processed {steps} steps!",
            "new_level": player.level
        })
    else:
        return JsonResponse({"status": "Error", "message": "Failed to process stats."})

@login_required
def sync_google_fit(request):
    player = PlayerProfile.objects.get(user=request.user)
    if not player.google_refresh_token:
        return redirect('google_fit_login')
    creds_dict = {                                  # 1. Prepare credentials from the database
        'token': player.google_access_token,
        'refresh_token': player.google_refresh_token,
        'token_uri': player.google_token_uri,
        'client_id': player.google_client_id,
        'client_secret': player.google_client_secret,
    }
    try:                                            # 2. Fetch steps from Google Fit
        real_steps = FitService.get_steps(creds_dict)
        step_log, created = DailyStepLog.objects.get_or_create(
            user=request.user,
            date=date.today(),
            defaults={'steps': real_steps, 'is_processed': False}
        )
        if not step_log.is_processed:
            step_log.steps = real_steps             # Update steps if refreshed
            step_log.save()
            process_daily_steps(player, step_log)
            messages.success(request, f"Synced {real_steps} steps! Your legend grows.")
        else:
            messages.info(request, "Today's deeds are already written in the stars.")
            
        return redirect('dashboard')
        
    except Exception as e:
        print(f"Error syncing Fit: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"Connection to Google Fit lost ({str(e)}). Please re-link your account.")
        return redirect('dashboard')

@login_required
def unsync_google_fit(request):
    player = PlayerProfile.objects.get(user=request.user)
    player.google_access_token = None
    player.google_refresh_token = None
    player.google_token_uri = None
    player.google_client_id = None
    player.google_client_secret = None
    player.save()
    messages.success(request, "Google Fit disconnected successfully. Take a rest, hero!")
    return redirect('dashboard')

@login_required
def sync_and_generate(request):
    player = PlayerProfile.objects.get(user=request.user)
    old_location = player.current_location
    latest_log = DailyStepLog.objects.filter(user=player.user, is_processed=False).last()
    if latest_log:
        process_daily_steps(player, latest_log)
        if player.current_location != old_location:
            messages.success(request, f"🗺️ NEW REGION UNLOCKED: Welcome to {player.current_location}!")
    return redirect('dashboard')
    
@login_required
def adventure_log(request):
    from collections import OrderedDict
    stories = DailyStory.objects.filter(player__user=request.user).order_by('date')
    # Group stories into arcs by world_region
    arcs = OrderedDict()
    for story in stories:
        region = story.world_region or "Unknown Realm"
        if region not in arcs:
            arcs[region] = {
                'region': region,
                'location': story.location_name or "Uncharted Lands",
                'stories': [],
            }
        arcs[region]['stories'].append(story)
    # Reverse the arcs so newest region comes first
    reversed_arcs = OrderedDict(reversed(list(arcs.items())))
    
    return render(request, 'tracker/adventure_log.html', {'arcs': reversed_arcs})