import uuid

from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage

from django.contrib.auth.decorators import login_required

from django.contrib import messages
from .models import EmailVerificationCode, Profile, BrokerageAccount, Holding, PortfolioTime
from django.core.mail import send_mail
from random import randint
from django.conf import settings
# Create your views here.
from django.db.models.signals import post_save
# We don't wanna use float, as it's inaccurate.
from decimal import Decimal



import secrets


from snaptrade_client import SnapTrade
import twelvedata
from twelvedata import TDClient


import json
from django.http import JsonResponse

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from finnhub import Client

from allauth.socialaccount.signals import social_account_added

from datetime import datetime, date

from dateutil.relativedelta import relativedelta
import requests

import fmpsdk

import marketstack

from yahooquery import Ticker, Screener
from django.dispatch import receiver
from dotenv import load_dotenv
import os
from .KOSAI import(
    snaptrade_account_register,
    snaptrade_portfolio
)


from .financial_service import (
    stock_data,
    dailyWinners,
    dailyLosers,

    get_company_name
)
from .insider_transaction import(
    insider_recent_trader,
    insider_transaction_trading_sentiment,
)
from .KOSAI import sync_to_snaptrade

from . financial_models import(
    bullish_indicator,
)

from .search_engine import(
    ticker_exists_database
)




from .news import top_news, stock_news

load_dotenv()






# REFERENCE: https://docs.snaptrade.com/docs/getting-started
# https://pypi.org/project/snaptrade-python-sdk/


CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

FINNHUB_API = os.getenv('FINNHUB_KEY')

API_KEY = os.getenv('ALPACA')
ALPACA_SECRET_KEY  = os.getenv('ALPACA_SECRET_KEY')
TWELVEDATA_API_KEY = os.getenv('TWELVEDATAAPI')





# MarketStack client



FINANCIAL_API_KEY = os.getenv("FINANCIAL_API_KEY")



finnhub_client = Client(api_key=FINNHUB_API)


tickers = []

SnapTradeAPI_ACTIVATE  = SnapTrade(client_id=CLIENT_ID, consumer_key=SECRET_KEY)
# Plans: First we need to have our signup/authentication systems ready at any cost,
CLIENT_FINANCE = fmpsdk.gainers(apikey=FINANCIAL_API_KEY)


CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
snaptrade = SnapTrade(
    client_id=CLIENT_ID,
    consumer_key=SECRET_KEY,
)


# Create a autosign up to SnapTrade


# Grab the user's portfolio, and we'll have a error handling that will ensure if there's a case where the User hasn't registered


# rEFERENCE: http://pypi.org/project/snaptrade-python-sdk/#snaptradeaccount_informationget_user_holdings




# Referenece: https://marketstack.com/documentation
# https://github.com/wsbinette/marketstack-api


def dailyWinners():
    try:
        s = Screener()
        stocks = s.get_screeners(['day_gainers'], count=5)
        gainers_list = stocks.get('day_gainers', {}).get('quotes', [])
        sorted_gainers = sorted(
            gainers_list, 
            key=lambda x: x.get('regularMarketChangePercent', 0), 
            reverse=True
        )

        # Prepare it for JSON dump and call it in search views.py
        result = []
        for symbols in sorted_gainers:
            symbol = symbols.get('symbol')
            percentage = symbols.get('regularMarketChangePercent')
            price = Ticker(symbol)

            hist = price.history(period='1d', interval='15m').reset_index()
            price = hist["close"].tolist()
            result.append({
                'ticker':  symbol,
                'price': price,
                'percent': round(float(percentage), 2)

            })
            

    
        return result
    except Exception as e:
        return []  # Return an empty list in case of any error, such as that we can raise API limit error or something like that, so we can just return an empty list and it won't break the website, and we can also add a message to the user that there's a issue with the API and that they should try again later.

def dailyLosers():
    try:

        s = Screener()
        stocks = s.get_screeners(['day_losers'], count=5)
        gainers_list = stocks.get('day_losers', {}).get('quotes', [])
        sorted_gainers = sorted(
            gainers_list, 
            key=lambda x: x.get('regularMarketChangePercent', 0), 
            reverse=False
        )

        # Prepare it for JSON dump and call it in search views.py
        result = []
        for stock in sorted_gainers:
            symbol = stock.get('symbol')
            percentage = stock.get('regularMarketChangePercent')
            price = Ticker(symbol)

            hist = price.history(period='1d', interval='15m').reset_index()
            price = hist["close"].tolist()
            result.append({
                'ticker':  symbol,
                'price': price,
                'percent': round(float(percentage), 2)

            })
        return result
    except Exception as e:
        return []  # Return an empty list in case of any error, such as that we can raise API limit error or something like that, so we can just return an empty list and it won't break the website, and we can also add a message to the user that there's a issue with the API and that they should try again later.






def signup_page(request):
    # If the user is already logged in, we'll just put them redirect them to the portfolio setting.
    if request.user.is_authenticated:
        return redirect('home')

    # Signup
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.is_active:
                return redirect('login')
            else:
                user = existing_user

        # Then we should redirect the user to verification code and match it email
        else:
            # We should also build an absoloute url for security purposes, 
            user = User.objects.create_user(username=username, password=password, email=email)
            # They're not verified, and they'll have to do it through the built in url
            user.is_active = False
            user.save()

            profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'is_verified': False}
        )
            if not created:
                profile.is_verified = False
                profile.save()
            if user and user.is_active:
                return redirect("login")


        # So we wanna generate the verification code
        generated_code = f"{secrets.randbelow(1_000_000):06}"
        
        
        # After that we wanna create the model of email verification and we can do a if-statement to check if the email verification is matched with the user
        
        EmailVerificationCode.objects.update_or_create(user=user, defaults={'code': generated_code, 'is_verified': False})

        request.session['verify_user_id'] = user.id

        try:

            send_mail(
                subject="Verify your code",
                message=f"Hello {user.username}, your verification code is {generated_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('verify')
        except Exception as e:
            messages.error(request, f"Email failed: {e}")
            return redirect('signup')
            

    return render(request, 'base/authentication/signup.html')
# This will be our API call towards Google for users to login via this method

# TODO: Add login with google URl method, and it will bypass the verifcation code since we know that user email exists and that all we need to do is just have the user make a username and then -> 
@login_required
def snaptrade_account_register(user):
    # If the user exist just return, so we don't get duplicate
    profile, created = Profile.objects.get_or_create(user=user)
    if  profile.snaptrade_user_id:
        return
    snaptrade_user_id = f"user_{user.id}_{uuid.uuid4().hex[:8]}"
    response = SnapTradeAPI_ACTIVATE.authentication.register_snap_trade_user(
    user_id=snaptrade_user_id
)
    profile.snaptrade_user_id = snaptrade_user_id
    profile.snaptrade_user_secret = response.body["userSecret"]
    profile.save()


@receiver(social_account_added)
def email_google_activation(request, sociallogin, **kwargs):
    # Create the account for them and create profile
    user = sociallogin.user
    # Create the profile
    profile, _ = Profile.objects.get_or_create(user=user)

    profile.is_verified = True
    profile.save()

    user.is_active = True
    user.save()
    
    try:
        snaptrade_account_register(user)
    except Exception as e:
        print(f"SnapTrade registration failed for user {user.username}: {e}")
        
    
@receiver(social_account_added)
def email_microsoft_activation(request, sociallogin, **kwargs):
    # Create the account for them and create profile
    
    user = sociallogin.user
    
    # Create the profile
    profile, _ = Profile.objects.get_or_create(user=user)

    profile.is_verified = True
    profile.save()

    user.is_active = True
    user.save()
    
    try:
        snaptrade_account_register(user)
    except Exception as e:
        print(f"SnapTrade registration failed for user {user.username}: {e}")
        
    
        
    
    
    


# Create a views where the user can enter their StockPortfolio signup to Wealthsimple, Shakepay, etc.



def verification_page(request):
    # This is where we'll send the verification code
    # and we also need the verification code here to match with user's connected email.
    
    if request.method == 'POST':
        code = request.POST.get('code')
        user_id = request.session.get('verify_user_id')
        # If empty redirect to signup
        if not user_id:
            return redirect('signup')
    
        try:
            verification = EmailVerificationCode.objects.get(
                user_id=user_id,
                code=code
            )
            # Check if it's expired if it is it will redirect to signup
            if verification.is_expired():
                verification.delete()
                messages.error(request, "Verification code expired.")
                return redirect('signup')
            user = verification.user
            profile, created = Profile.objects.get_or_create(user=user)
            profile.is_verified = True
            profile.save()
           
            user.is_active = True
            user.save()


            verification.delete()
            # Register for it after the user has verified
            snaptrade_account_register(user)
            # Clarify the backend
            user.backend =  'kentrocenterback.backend.EmailBackend'

            login(request, user)

            return redirect('home')
        # Signup would be required as if someone tried to do a url /verification/ it would have a messages.error

        except EmailVerificationCode.DoesNotExist:
            messages.error(request, "Verification Code does not Exist, Please Signup")
            return redirect('signup')
    return render(request, 'base/verification.html')
    
def home(request):
    # We want this to be our portfolio view, but first we might wanna do is connect our API/investment platform!
    
    # Have our dailyWnners and Daily losers at the start, similar to our
    daily_winners = dailyWinners()
    daily_losers = dailyLosers()
    # Json dump so that info is able to be reliable and seamless data transfer to Javascript
    # which will be used for Chart.JS
    percentage_losing = json.dumps([tickers["price"] for tickers in daily_losers])
    percentage_winners = json.dumps([tickers["price"] for tickers in daily_winners])

    ticker_of_winners = json.dumps([tickers["ticker"] for tickers in daily_winners])
    ticker_of_losers =  json.dumps([tickers["ticker"] for tickers in daily_losers])
    
    
    context = {
        "gainers": daily_winners,
        "losers": daily_losers,
        "label_ticker_winners": ticker_of_winners,
        "label_ticker_losers": ticker_of_losers,
        "percentage_winners": percentage_winners,
        "percentage_losing": percentage_losing,
        "news_information" : top_news()

    }
 


    return render(request, 'base/home.html', context)



def stock(request, stock_ticker:str):
    # Because we want to have it valid such as that aapl -> AAPL to grab the data easily
    stock_url = stock_ticker.upper()
    
    # Grab stock data
    
    stock_ticker_data = stock_data(stock_url)
    # Get the price history
    
    price_history =  json.dumps(stock_ticker_data.get("price", []))
    labels =  json.dumps(stock_ticker_data.get("labels", []))
    
    # Grab news for the stock and the seniment score for the news
    stock_news_data = stock_news(stock_url)

    
    
    # Grab insider trading information for the stock, LEGAL OFC, IT'S FROM THE SEC LOL

    insider_transaction_data_sentiment = insider_transaction_trading_sentiment(stock_url)
    
    current_price = stock_ticker_data['stock_price']
    
    bearish_indicator = bullish_indicator(stock_url)
    
    
    percentage = stock_ticker_data['percentage']
    company_name = get_company_name(stock_ticker)
    
    
    context = {
        "stock_ticker": stock_url,
        "price_history": price_history,
        "labels": labels,
        "stock_news_data": stock_news_data,
        'insider_transaction_data_sentiment': insider_transaction_data_sentiment,
        'insider_recent_trader': insider_recent_trader(stock_url),
        "bullish_indicator": bullish_indicator(stock_url),
        "bearish_indicator":  100 - bearish_indicator, 
        'current_price': round(current_price,2),
        'percent_change': round(percentage,2),
        "name": company_name
        
    }
    return render(request, 'base/stock_view.html', context)
    
  






    
    # Grab the data for the insider trading and store it in a json_information

    


    


def redirect_url_snaptrade(request):
    status = request.GET.get("status")
    if status == "SUCCESS":
        sync_to_snaptrade(request.user)
        return redirect("home")
     
    messages.warning(request, f"Connection status: {status or 'Cancelled'}")
    return redirect("home")





def search_views(request):
    try:
        search = request.GET.get("search")

        if search:
            search_stock = search.upper()

            exists = ticker_exists_database(search_stock)

            if exists is None:
                messages.error(request, "API Error")
            elif exists is False:
                messages.error(request, "Stock Does not Exist")
            else:
                return redirect('stock', stock_ticker=search_stock)

        # Always render page if no valid redirect
        return render(request, 'base/search_engine_views.html')

    except Exception:
        messages.error(request, "Server Issue: Error Code 404")
        return redirect("home")
    






# We'd want to JSON Serialize this one on home views




# TODO; Snaptrade link account
def snaptrade_link_views_wealthsimple(request):
    profile = request.user.profile
    


    if not profile.snaptrade_user_id or not profile.snaptrade_user_secret:
        messages.error(request, "SnapTrade account not initialized.")
        return redirect("home")

    try:
        
        url_redirecter_to_kentrocherma = request.build_absolute_uri(reverse('snaptrade_callback'))

        
        login_link = SnapTradeAPI_ACTIVATE.authentication.login_snap_trade_user(
            user_id=profile.snaptrade_user_id,
            user_secret=profile.snaptrade_user_secret,
            # Use custom_redirect
            
            custom_redirect=url_redirecter_to_kentrocherma,
        )

        redirect_uri = login_link.body.get("redirectURI")

        if not redirect_uri:
            messages.error(request, "SnapTrade failed to generate link.")
            return redirect("home")



        return redirect (redirect_uri)
    
    
    

    except Exception as e:
        print("SnapTrade ERROR:", e)
        messages.error(request, "SnapTrade connection failed.")
        return redirect("home")


 
# This will be the secondary process after the User has linked their bank accounts
def account_link_porfolio(request):
    user = request.user
    # Must have a snaptrade_user
    if not user.profile.snaptrade_user_id:
        messages.error(request, "SnapTrade account not initialized.")
        return redirect('home')


    
def user_portfolio(request):
    # Now for this one we gotta grab our snaptrade user id and also grab portfolio models and holdings models and then we can display it on the portfolio page, and we can also have a error handling that will ensure if there's a case where the User hasn't registered or haven't synced their account, so we can just display a message that they should link their account to see their portfolio, and then we can have a button that will redirect them to the snaptrade_link_views_wealthsimple view that will allow them to link their account, and then after they link their account we can redirect them back to the portfolio page and then we can display their portfolio information, such as their total value and also their holdings and also the performance of their portfolio, such as how much they gained or lost in the last day or in the last week or in the last month, etc.
    
    profile = request.user.profile
    # We wanna warn user right, so we add swalfire for this one
    if not profile.snaptrade_user_id or not profile.snaptrade_user_secret:
        messages.warning(request, "Please link your SnapTrade account to view your portfolio.")
        return redirect('home')
    accounts = BrokerageAccount.objects.filter(snaptrade_user_id=profile.snaptrade_user_id)
    if not accounts.exists():  
        return redirect('home')
    

    
    return render(request, 'base/portfolio.html')

def loginpage(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)


        if user is not None:
            # check if they're veriified
            if not user.is_active:
                messages.warning(request, "Please verify your email first.")
                return redirect('verify')
            
            # Clarify backend, as there's a issue and Django complains about it
            user.backend =  'kentrocenterback.backend.EmailBackend'
            login(request, user)
            return redirect('home')
        else:
            # Invalid password case
            messages.error(request, "Invalid password.")
            return render(request, 'base/login.html') # Stay here
            
    return render(request, 'base/authentication/login.html')





def logout_page(request):
    logout(request)
    return redirect('signup')