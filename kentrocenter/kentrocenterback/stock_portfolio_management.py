#  This is for the financial item model, which will be used to store the financial items for the users., and we're also looking at sentiments from the insider
import twelvedata
from datetime import date
from dateutil.relativedelta import relativedelta
from twelvedata import TDClient
from snaptrade_client import SnapTrade



import finnhub
from finnhub import Client
import os
from dotenv import load_dotenv
import ta
import pandas as pd
from yahooquery import Screener, Ticker

from .models import BrokerageAccount, Holding, PortfolioTime


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


def sync_to_snaptrade(user):
    # This is for the sync to snaptrade, which will be used to sync the user's brokerage account to snaptrade, and we'll use the snaptrade API to do this, and we'll also use the snaptrade API to grab the user's portfolio and holdings, and we'll store that in our database so that we can use it for our portfolio page and also for our financial models.
    profile = user.profile
    if not profile.snaptrade_user_id or not profile.snaptrade_user_secret:
        return
    snaptrade_user_id = profile.snaptrade_user_id
    snaptrade_user_secret = profile.snaptrade_user_secret
    accounts = SnapTradeAPI_ACTIVATE.account_information.list_user_accounts(
        user_id=profile.snaptrade_user_id, 
        user_secret= profile.snaptrade_user_secret)
    
    total_value = 0
    for account in accounts:
        brokage_link_sync, _ = BrokerageAccount.objects.update_or_create(
            account_id=account.account_id,
            defaults={
                "snaptrade_user_id": snaptrade_user_id,
                "snaptrade_user_secret": snaptrade_user_secret,
            }
        )
        # Clear old holdings for this account before syncing new ones
        Holding.objects.filter(user=brokage_link_sync).delete()
        
        holdings = SnapTradeAPI_ACTIVATE.holdings.list_holdings(
            user_id=snaptrade_user_id, 
            user_secret= snaptrade_user_secret, 
            account_id=account.account_id
        )
        positions = holdings.get("data", {}).get("positions", [])
        for position in positions:
            book_cost = position.get("book_cost", 0)
            shares_hold = position.get("shares", 0)
            market_value = position.get("market_value", 0)
            total_value += market_value
            Holding.objects.create(
                user=brokage_link_sync,
                book_cost=book_cost,
                shares_hold=shares_hold,
                market_value=market_value
            )
            
        PortfolioTime.objects.create(
            user=user,
            total_value=total_value
        )
        
        
def portfolio():
    pass
        
        
    
    # Now we have to use the snaptrade API to grab the user's portfolio and holdings, and we'll store that in our database so that we can use it for our portfolio page and also for our financial models.
    # Register the snaptrade information portfolio and holdings to our database, and we'll also update the snaptrade information in our database so that we can use it for our portfolio page and also for our financial models.


def sharpe_ratio(portfolio: dict) -> float:
    pass