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
def user_portfolio(request):
    # Update the user
    sync_to_snaptrade(request.user)
    # Accesst he user

    accounts = request.user.brokerage_accounts.all()

    if not accounts.exists():
        return redirect("home")

    holdings = (
        Holding.objects
        .filter(brokerage_account__in=accounts)
        .values("ticker")
        #Group 1 → AAPL

# Group 2 → TSLA
# SPLIT THEM ALL IN GROUPS AS WE DON'T WANT THEM TO LIKE MERGE TGOETHER, IT'S THE LAST THING WE WANT!
        .annotate(
            total_shares=Sum("shares_hold"),
            total_market_value=Sum("market_value"),
            total_book_cost=Sum("book_cost"),
        )
        .order_by("-total_market_value")
    )

    # Decimal is much more accurate than Float (THanks a lot CPSC 217 lollll)
    total_value = Decimal("0")
    total_gain_loss = Decimal("0")
    # iterate through holdings, etc.

    for h in holdings:
        print("Ticker:", h["ticker"])
        print("Market:", h["total_market_value"])
        print("Book:", h["total_book_cost"])
        total_value += h["total_market_value"]
        gain = h["total_market_value"] - h["total_book_cost"]
        h["gain_loss"] = gain
        total_gain_loss += gain
        
        # Grab the book cost, such as that how much has the person make as book cost is how much
        # average worth is their stock (including DCA)

        if h["total_book_cost"] > 0:
            h["gain_percent"] = (gain / h["total_book_cost"]) * 100
        else:
            h["gain_percent"] = Decimal("0")
    # Context for JS, so we can create a graph

    context = {
        "holdings": holdings,
        "total_value": total_value,
        "total_gain_loss": total_gain_loss,
    }
    
    print(context)

    return render(request, "base/portfolio.html", context)

        
    #OUTPUT: {'holdings': <QuerySet [{'ticker': "{'id': 'c31e2d7a-5f87-4305-9867-56a01ccfd09d', 'symbol': 'BTC', 'description': 'Bitcoin', 'currency': {'code': 'USD', 'name': 'US Dollar', 'id': '57f81c53-bdda-45a7-a51f-032afd1ae41b'}, 'exchange': {'id': 'fb222c8b-3746-4555-b9d4-b238dcc3230a', 'code': 'COIN', 'mic_code': None, 'name': 'Coinbase', 'suffix': None, 'timezone': 'America/New_York', 'start_time': '00:00:00', 'close_time': '23:59:59.999999'}, 'currencies': [], 'type': {'id': '8c76d59d-1214-4412-9526-052412392387', 'code': 'crypto', 'description': 'Cryptocurrency', 'is_supported': True}, 'raw_symbol': 'BTC', 'logo_url': None, 'figi_code': 'KKG000000M81', 'figi_instrument': {'figi_code': 'KKG000000M81', 'figi_share_class': None}}", 'total_shares': Decimal('0.997500000000000'), 'total_market_value': Decimal('0'), 'total_book_cost': Decimal('63443.1122203846'), 'gain_loss': Decimal('-63443.1122203846'), 'gain_percent': Decimal('-100')}]>, 'total_value': Decimal('0'), 'total_gain_loss': Decimal('-63443.1122203846')}

    
    # Now we have to use the snaptrade API to grab the user's portfolio and holdings, and we'll store that in our database so that we can use it for our portfolio page and also for our financial models.
    # Register the snaptrade information portfolio and holdings to our database, and we'll also update the snaptrade information in our database so that we can use it for our portfolio page and also for our financial models.


def sharpe_ratio(portfolio: dict) -> float:
    pass