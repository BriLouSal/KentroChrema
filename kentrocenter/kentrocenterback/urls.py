from django.urls import path, include
from django.conf import settings
from . import views


urlpatterns  = [
    path('', views.home, name='home'),
    
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]