from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from . import views, search_engine, stock_orders, stock_portfolio_management


urlpatterns  = [
    
    path(
        "accounts/3rdparty/login/cancelled/",
        lambda request: redirect("signup"),
    ),
    path('', views.signup_page, name='signup'),
    
    path('home/', views.home, name='home'),
    
    
    path('login/' , views.loginpage, name='login'),
    
    path('verification/', views.verification_page, name='verify'),
    
    path('portfolio/', stock_portfolio_management.user_portfolio, name='portfolio'),
    
    path('stock/<str:stock_ticker>/', views.stock, name='stock'),
    
    path('logout/', views.logout_page, name='logout'), 
    
    path('snaptrade_verification/', views.snaptrade_link_views_wealthsimple, name='snaptrade_link'),
    path('search_views/', views.search_views, name='search_views'),
    
    path('snaptrade_callback/', views.redirect_url_snaptrade, name='snaptrade_callback'),
   
    # API and Login methods
    path("api/autocomplete/<str:letters>/", search_engine.information_letter, name="information_letter"),
    
    path('api/order/', stock_orders.stock_order , name='stock_order'),
    
    path('accounts/', include('allauth.urls')),
    
    
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    
    
