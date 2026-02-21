from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from .models import EmailVerificationCode, Profile
from django.core.mail import send_mail
from random import randint
from django.conf import settings
# Create your views here.
from django.db.models.signals import post_save
# We don't wanna use float, as it's inaccurate.
from decimal import Decimal



from snaptrade_client import SnapTrade
from marketstack.api.intraday import intraday
import marketstack

import json
from django.http import JsonResponse

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from finnhub import Client

from allauth.socialaccount.signals import social_account_added

from datetime import datetime, date

from dateutil.relativedelta import relativedelta


import fmpsdk


from yahooquery import Ticker, Screener
from django.dispatch import receiver
from dotenv import load_dotenv
import os
from .KOSAI import(
    snaptrade_account_register,
    snaptrade_portfolio
)

load_dotenv()






# REFERENCE: https://docs.snaptrade.com/docs/getting-started
# https://pypi.org/project/snaptrade-python-sdk/


CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

FINNHUB_API = os.getenv('FINNHUB_KEY')

API_KEY = os.getenv('ALPACA')
ALPACA_SECRET_KEY  = os.getenv('ALPACA_SECRET_KEY')
MARKETSTACK_API = os.getenv('MARKETSTACK_API_KEY')




# MarketStack client

def create_client() -> tuple[Client, str]:  
    access_key = os.getenv("MARKETSTACK_API_KEY")
    client = Client(base_url="https://api.marketstack.com/v1", headers={"Authorization": f"Bearer {access_key}"})
    
    return client, access_key 

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




# Referenece: https://pypi.org/project/marketstack/
# https://github.com/mreiche/marketstack-python/
def stock_data(stock_ticker: str):
    # I shall use marketstack for this one, as it has a lot of data and it's free, and it also has a python wrapper which is really good for us to use. and it's much more stable than Yahoo finance
    client, access_key = create_client()
    mapping = {
        '1D': {'interval': '15min', 'limit': 100},
        '1W': {'interval': '1hour', 'limit': 200},
        '1M': {'interval': '12hour', 'limit': 300},
        '1Y': {'interval': '24hour', 'limit': 365}
    }

    configuration = mapping.get('1D', {'interval': '15min', 'limit': 100}) 
        
    stock_ticker = stock_ticker.upper()
    try:
        response = intraday.sync(
            client=client,
            access_key=access_key,
            symbols=stock_ticker,
            interval=configuration['interval'],
            limit=configuration['limit']
        )
        
        if response.status_code != 200:
            print(f"Error fetching stock data: {response.status_code} - {response.text}")
            return None
        
        price_graph = [item.last for item in reversed(response)]
        price_label = [item.date.strftime("%Y-%m-%d %H:%M") for item in reversed(response)]
        
        
        return {
            "price_graph": price_graph,
            "price_label": price_label
        }
    except Exception as e:
        print(f"Error fetching stock data for {stock_ticker}: {e}")
        return None  # Return None or an appropriate value to indicate failure
    


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
        generated_code = str(randint(100000, 999999))
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

@receiver(social_account_added)
def email_google_activation(sender, request, sociallogin, **kwargs):
    # Create the account for them and create profile
    user = sociallogin.user
    # Create the profile
    profile, created = Profile.objects.get_or_create(user=user)

    profile.is_verified = True
    profile.save()

    user.is_active = True
    user.save()


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
            user.backend = settings.AUTHENTICATION_BACKENDS[0]

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
        "news_information" : top_news(),

    }
 


    return render(request, 'base/home.html', context)



def stock(request, stock_ticker:str):
    # Because we want to have it valid such as that aapl -> AAPL to grab the data easily
    stock_url = stock_ticker.upper()
    
    return render(request, 'base/stock_view.html')
    
    

def insider_transaction_trading(stock_ticker: str,):
    stock_ticker = stock_ticker.upper()
    
    today = date.today().isoformat()

    insider_informtion = []

    one_month_ago = (date.today() - relativedelta(months=12)).isoformat()
    
    
    sentiment_data = finnhub_client.stock_insider_sentiment(symbol=stock_ticker, to=today, _from=one_month_ago)
    
    # Grab the data for
    for data in sentiment_data.get("data", []):
        insider_informtion.append({
            "mspr": data.get("mspr"),
        })
        
    
    
        
    
    
    
    
    
    
    
    return sentiment_data


def redirect_url_snaptrade(request):
    status = request.GET.get("status")
    if status == "SUCCESS":
        return redirect("home")
    messages.warning(request, f"Connection status: {status or 'Cancelled'}")
    return redirect("home")





def stock_news(data):
    pass

# We'd want to JSON Serialize this one on home views

def top_news():
    # So we know it returns a Json data, so we'll have to iterate through it and make some empty list
    sentiment_score = SentimentIntensityAnalyzer()
    finnhub_client_news = finnhub_client.general_news('crypto', min_id=0)
    news_data = []
    for news in finnhub_client_news:
        headline = news.get("headline", "")
    
        
        news_data.append({
            "headline": news["headline"],
            "summary": news["summary"],
            "link": news['url'],
            "sentiment_score": sentiment_score.polarity_scores(headline)["compound"],
            # use absolute polarity score and we'll sort it via lambda
            "impact_score": abs(sentiment_score.polarity_scores(headline)["compound"]),
        
            
        })
        # Sort it via the biggest imapct score, we'll use absolute numbers for this one 
        # so we can have the highest impacts as possible -99.3 -> 99.3
        
        sorted_news = sorted(
            news_data,
            key=lambda x: x["impact_score"],
            reverse=True,
        )
        
    return sorted_news[:5]





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

        print("SnapTrade response:", login_link.body) 

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
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
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