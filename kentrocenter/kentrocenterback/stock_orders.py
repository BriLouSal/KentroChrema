#  This is for the financial item model, which will be used to store the financial items for the users., and we're also looking at sentiments from the insider
import twelvedata
from datetime import date
from dateutil.relativedelta import relativedelta
from twelvedata import TDClient
from snaptrade_client import SnapTrade

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
from django.http import JsonResponse

from django.db.models import Sum


import finnhub
from finnhub import Client
import os
from dotenv import load_dotenv
import ta
import pandas as pd
from yahooquery import Screener, Ticker

from .KOSAI import sync_to_snaptrade

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

FINNHUB_API = os.getenv('FINNHUB_KEY')

API_KEY = os.getenv('ALPACA')
ALPACA_SECRET_KEY  = os.getenv('ALPACA_SECRET_KEY')
TWELVEDATA_API_KEY = os.getenv('TWELVEDATAAPI')


finnhub_client = Client(api_key=FINNHUB_API)

TWELVEDATA_API_KEY = os.getenv('TWELVEDATAAPI')


# Plans: First we need to have our signup/authentication systems ready at any cost,


CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

SnapTradeAPI_ACTIVATE  = SnapTrade(client_id=CLIENT_ID, consumer_key=SECRET_KEY)



        
@login_required
def stock_order(request, ticker: str):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    profile = request.user.profile

    if not profile.snaptrade_user_id or not profile.snaptrade_user_secret:
        return JsonResponse({"error": "SnapTrade not linked"}, status=400)

    account = BrokerageAccount.objects.filter(user=request.user).first()

    if not account:
        return JsonResponse({"error": "No brokerage account found"}, status=400)

    action = request.POST.get("action")
    order_type = request.POST.get("order_type")
    quantity = request.POST.get("quantity")
    limit_price = request.POST.get("limit_price")

    if action not in ["BUY", "SELL"]:
        return JsonResponse({"error": "Invalid action"}, status=400)

    if order_type not in ["Market", "Limit"]:
        return JsonResponse({"error": "Invalid order type"}, status=400)

    try:
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError
    except:
        return JsonResponse({"error": "Invalid quantity"}, status=400)

    payload = {
        "user_id": profile.snaptrade_user_id,
        "user_secret": profile.snaptrade_user_secret,
        "account_id": account.account_id,
        "action": action,
        "symbol": ticker.upper(),
        "order_type": order_type,
        "time_in_force": "Day",
        "trading_session": "REGULAR",
        "units": quantity,
    }

    if order_type == "Limit":
        try:
            payload["price"] = float(limit_price)
        except:
            return JsonResponse({"error": "Invalid limit price"}, status=400)

    try:
        response = SnapTradeAPI_ACTIVATE.trading.place_order(**payload)

        # Immediately resync portfolio
        sync_to_snaptrade(request.user)

        return JsonResponse({
            "success": True,
            "message": "Order placed successfully",
            "order": response.body
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
        

    
    # Now we have to use the snaptrade API to grab the user's portfolio and holdings, and we'll store that in our database so that we can use it for our portfolio page and also for our financial models.
    # Register the snaptrade information portfolio and holdings to our database, and we'll also update the snaptrade information in our database so that we can use it for our portfolio page and also for our financial models.




