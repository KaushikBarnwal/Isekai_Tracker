from django.urls import path
from . import views

urlpatterns = [
    path('login-fit/', views.google_fit_login, name='google_fit_login'),
    path('callback/', views.google_fit_callback, name='google_fit_callback'),
    path('sync/', views.sync_google_fit, name='sync_google_fit'),
    path('unsync/', views.unsync_google_fit, name='unsync_google_fit'),
    path('chronicles/', views.adventure_log, name='adventure_log'),
    # Test Trigger (keep for debugging)
    path('test/<int:player_id>/<int:steps>/', views.test_isekai_trigger, name='test_trigger'),
]