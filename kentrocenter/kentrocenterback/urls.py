from django.urls import path, include
from django.conf import settings
from . import views


urlpatterns  = [
    path('', views.signup_page, name='signup'),
    path('home/', views.home, name='home'),
    path('login/' , views.login, name='login'),
    path('verification/', views.verification_page, name='verify'),
    
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]