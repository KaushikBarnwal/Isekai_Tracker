"""
URL configuration for isekai_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth.models import User
from django.http import HttpResponse

def temporary_admin_tool(request):
    username_to_set = "admin"
    password_to_set = "hihihi" # Change this to what you want
    email_to_set = "barnwalkaushik@gmail.com"
    user, created = User.objects.get_or_create(
        username=username_to_set, 
        defaults={'email': email_to_set}
    )
    user.set_password(password_to_set)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    if created:
        return HttpResponse(f"Successfully created superuser '{username_to_set}' with your password!")
    return HttpResponse(f"Successfully overwrote password for existing user '{username_to_set}'!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('tracker.urls')),
    path('', include('players.urls')),
    path('secure-cloud-admin-setup-777/', temporary_admin_tool),
]
