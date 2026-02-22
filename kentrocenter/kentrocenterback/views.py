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






def stock_data(stock_ticker: str):
    # I shall use marketstack for this one, as it has a lot of data and it's free, and it also has a python wrapper which is really good for us to use. and it's much more stable than Yahoo finance
    twelvedata_client = TDClient(apikey=TWELVEDATA_API_KEY)
    
    try:
        
        ticker_data = twelvedata_client.time_series(
            symbol=stock_ticker.upper(),
            interval="1min",
            outputsize=100
            
        ).as_pandas()
        
        # We have to reverse the data so that we can have the most recent data at the end of the list, which will be used for Chart.JS
        ticker_data = ticker_data.iloc[::-1]

        price = [float(value) for value in ticker_data["close"].tolist()]
        
        labels = [timestamp.strftime("%Y-%m-%d %H:%M:%S") for timestamp in ticker_data.index]
        
        print("Price data:", price)
        print("Labels data:", labels)
     
     
        return {"price": price, "labels": labels}
        
        

            
        
        # Now we have to parse the data and grab the price and the date, and we'll have to reverse it as well so that we can have the most recent data at the end of the list, which will be used for Chart.JS\

            



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
        "stock_data": stock_data("AAPL")  

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
    print("Price history:", price_history)
    print("Labels:", labels)
    
    
    # Grab news for the stock and the seniment score for the news
    stock_news_data = stock_news(stock_url)
    
    
    
    # Grab insider trading information for the stock, LEGAL OFC, IT'S FROM THE SEC LOL
    insider_trading_data = insider_transaction_trading(stock_url)
    

    
    
    
    
    
    
    
    
    context = {
    }
    return render(request, 'base/stock_view.html', context)
    
    # Output: Price data: [263.815, 263.965, 264.10001, 264.125, 264.25, 264.14001, 264.185, 264.22501, 264.25, 264.42999, 264.62381, 264.60999, 264.51001, 264.54501, 264.45999, 264.29999, 264.24039, 264.01501, 264.14999, 264.10501, 264.09, 264.17999, 264.04999, 263.92999, 263.90021, 263.76001, 263.715, 263.79001, 263.715, 263.763, 263.9404, 263.845, 263.95999, 264.16, 264.09052, 264.17001, 264.14999, 264.20001, 264.27499, 264.17599, 264.22, 264.33649, 264.19, 264.33499, 264.26001, 264.38, 264.42001, 264.35001, 264.38, 264.42001, 264.42999, 264.45389, 264.5, 264.625, 264.60999, 264.51001, 264.44501, 264.34, 264.32501, 264.28, 264.10999, 263.82001, 263.89719, 263.67001, 263.62039, 263.61499, 263.64999, 263.53, 263.38501, 263.33011, 263.47501, 263.45001, 263.3577, 263.28, 263.20001, 263.215, 263.20001, 263.19, 263.24039, 263.4299, 263.28, 263.44, 263.40991, 263.50061, 263.65991, 263.75, 263.82999, 263.81, 263.72, 263.76999, 264.13, 264.42001, 264.10001, 264.1001, 264.42999, 264.57999, 264.625, 264.67001, 264.60001, 264.59]
# Labels data: ['2026-02-20 14:20:00', '2026-02-20 14:21:00', '2026-02-20 14:22:00', '2026-02-20 14:23:00', '2026-02-20 14:24:00', '2026-02-20 14:25:00', '2026-02-20 14:26:00', '2026-02-20 14:27:00', '2026-02-20 14:28:00', '2026-02-20 14:29:00', '2026-02-20 14:30:00', '2026-02-20 14:31:00', '2026-02-20 14:32:00', '2026-02-20 14:33:00', '2026-02-20 14:34:00', '2026-02-20 14:35:00', '2026-02-20 14:36:00', '2026-02-20 14:37:00', '2026-02-20 14:38:00', '2026-02-20 14:39:00', '2026-02-20 14:40:00', '2026-02-20 14:41:00', '2026-02-20 14:42:00', '2026-02-20 14:43:00', '2026-02-20 14:44:00', '2026-02-20 14:45:00', '2026-02-20 14:46:00', '2026-02-20 14:47:00', '2026-02-20 14:48:00', '2026-02-20 14:49:00', '2026-02-20 14:50:00', '2026-02-20 14:51:00', '2026-02-20 14:52:00', '2026-02-20 14:53:00', '2026-02-20 14:54:00', '2026-02-20 14:55:00', '2026-02-20 14:56:00', '2026-02-20 14:57:00', '2026-02-20 14:58:00', '2026-02-20 14:59:00', '2026-02-20 15:00:00', '2026-02-20 15:01:00', '2026-02-20 15:02:00', '2026-02-20 15:03:00', '2026-02-20 15:04:00', '2026-02-20 15:05:00', '2026-02-20 15:06:00', '2026-02-20 15:07:00', '2026-02-20 15:08:00', '2026-02-20 15:09:00', '2026-02-20 15:10:00', '2026-02-20 15:11:00', '2026-02-20 15:12:00', '2026-02-20 15:13:00', '2026-02-20 15:14:00', '2026-02-20 15:15:00', '2026-02-20 15:16:00', '2026-02-20 15:17:00', '2026-02-20 15:18:00', '2026-02-20 15:19:00', '2026-02-20 15:20:00', '2026-02-20 15:21:00', '2026-02-20 15:22:00', '2026-02-20 15:23:00', '2026-02-20 15:24:00', '2026-02-20 15:25:00', '2026-02-20 15:26:00', '2026-02-20 15:27:00', '2026-02-20 15:28:00', '2026-02-20 15:29:00', '2026-02-20 15:30:00', '2026-02-20 15:31:00', '2026-02-20 15:32:00', '2026-02-20 15:33:00', '2026-02-20 15:34:00', '2026-02-20 15:35:00', '2026-02-20 15:36:00', '2026-02-20 15:37:00', '2026-02-20 15:38:00', '2026-02-20 15:39:00', '2026-02-20 15:40:00', '2026-02-20 15:41:00', '2026-02-20 15:42:00', '2026-02-20 15:43:00', '2026-02-20 15:44:00', '2026-02-20 15:45:00', '2026-02-20 15:46:00', '2026-02-20 15:47:00', '2026-02-20 15:48:00', '2026-02-20 15:49:00', '2026-02-20 15:50:00', '2026-02-20 15:51:00', '2026-02-20 15:52:00', '2026-02-20 15:53:00', '2026-02-20 15:54:00', '2026-02-20 15:55:00', '2026-02-20 15:56:00', '2026-02-20 15:57:00', '2026-02-20 15:58:00', '2026-02-20 15:59:00']
    

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


def insider_transaction_trading(stock_ticker: str,):
    stock_ticker = stock_ticker.upper()
    
    today = date.today().isoformat()

    insider_informtion = []

    one_month_ago = (date.today() - relativedelta(months=12)).isoformat()
    
    
    insider_trading_info =  finnhub_client.stock_insider_transactions(symbol=stock_ticker, to=today, _from=one_month_ago)
    
    for insider in insider_trading_info.get("data", []):
        insider_informtion.append({
            "name": insider.get("name"),
            "relationship": insider.get("relationship"),
            "transactionDate": insider.get("transactionDate"),
            "transactionType": insider.get("transactionType"),
            "sharesTraded": insider.get("sharesTraded"),
            "sharePrice": insider.get("sharePrice"),
        })
        
        
    return insider_informtion




    
    # Grab the data for the insider trading and store it in a json_information

    
    
    


def redirect_url_snaptrade(request):
    status = request.GET.get("status")
    if status == "SUCCESS":
        return redirect("home")
    messages.warning(request, f"Connection status: {status or 'Cancelled'}")
    return redirect("home")





def stock_news(stock: str):
    sentiment_stock_score = SentimentIntensityAnalyzer()
    finnhub_client_stock_news = finnhub_client.company_news(stock, _from=(date.today() - relativedelta(days=7)).isoformat(), to=date.today().isoformat())
    stock_news_data = []
    
    for news in finnhub_client_stock_news:
        headline = news.get("headline", "")
        stock_news_data.append({
            "headline": news["headline"],
            "summary": news["summary"],
            "link": news['url'],
            "sentiment_score": sentiment_stock_score.polarity_scores(headline)["compound"],
        })
    sorted_stock_news = sorted(
        stock_news_data,
        key=lambda x: abs(x["sentiment_score"]),
        reverse=True,
    )
    return sorted_stock_news[:5]

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