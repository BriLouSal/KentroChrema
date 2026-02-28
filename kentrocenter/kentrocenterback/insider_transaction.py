#  This is for the financial item model, which will be used to store the financial items for the users., and we're also looking at sentiments from the insider
import twelvedata
from datetime import date
from dateutil.relativedelta import relativedelta
from twelvedata import TDClient
from snaptrade_client import SnapTrade


from datetime import datetime

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


def insider_recent_trader(stock_ticker: str):
    stock_ticker = stock_ticker.upper()
    
    today = date.today().isoformat()

    insider_informtion = []

    one_month_ago = (date.today() - relativedelta(months=12)).isoformat()
    
    
    insider_trading_info =  finnhub_client.stock_insider_transactions(symbol=stock_ticker, to=today, _from=one_month_ago)
    for insider in insider_trading_info.get("data", []):
        insider_informtion.append({
            "name": insider.get("name"),
            "transactionDate": insider.get("transactionDate"),
            "share": insider.get("share"),
            "sharesTraded": insider.get("sharesTraded"),
            "sharePrice": insider.get("transactionPrice"),
        })
        
    sorted_score = sorted(
        insider_informtion,
        key= lambda x: (x["sharePrice"] * x["share"]),
        reverse=True
    )
    
    # Use set as we don't want duplicate 
    unique_insiders = []
    
    set_of_sorted = set()
    
    # Ensure no duplicates of insider name does not exist, we don't want

    for set_numbers in sorted_score:
        if set_numbers['name'] not in set_of_sorted:
            unique_insiders.append(set_numbers)
            set_of_sorted.add(set_numbers["name"])
        if len(set_of_sorted) == 5:
            break
        
    return unique_insiders

def insider_transaction_trading_sentiment(stock_ticker: str,):
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

