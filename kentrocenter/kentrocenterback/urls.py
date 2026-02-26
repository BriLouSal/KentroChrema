from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from . import views


urlpatterns  = [
    
    path(
        "accounts/3rdparty/login/cancelled/",
        lambda request: redirect("signup"),
    ),
    path(
        "http://127.0.0.1:8000/accounts/google/login/callback/?state=FqveawNTbM13GwXi&iss=https%3A%2F%2Faccounts.google.com&code=4%2F0AfrIepCoYUuDXkhrpK9PjHF64QlAzTo9vD7ZhQUQHrvt3suoABj4GpmPX3k5KiWwMIvLFQ&scope=email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+openid&authuser=1&prompt=none",
        lambda request: redirect('signup')
    ),
    
    
    path('', views.signup_page, name='signup'),
    path('home/', views.home, name='home'),
    path('login/' , views.loginpage, name='login'),
    path('verification/', views.verification_page, name='verify'),
    path('portfolio/', views.user_portfolio, name='portfolio'),
    path('stock/<str:stock_ticker>/', views.stock, name='stock'),
    path('logout/', views.logout_page, name='logout'),
    path('snaptrade_verification/', views.snaptrade_link_views_wealthsimple, name='snaptrade_link'),
    path('snaptrade_callback/', views.redirect_url_snaptrade, name='snaptrade_callback'),
    # API and Login methods
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    
    
