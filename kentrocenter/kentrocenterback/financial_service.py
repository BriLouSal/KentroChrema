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



def stock_data(stock_ticker: str):
    # I shall use TwelveData for this one, as it has a lot of data and it's free, and it also has a python wrapper which is really good for us to use. and it's much more stable than Yahoo finance
    twelvedata_client = TDClient(apikey=TWELVEDATA_API_KEY)
    
    try:
        
        ticker_data = twelvedata_client.time_series(
            symbol=stock_ticker.upper(),
            interval="5min",
            outputsize=78
            
        ).as_pandas()
        
  
        # We have to reverse the data so that we can have the most recent data at the end of the list, which will be used for Chart.JS
        ticker_data = ticker_data.iloc[::-1]

        # grab ticker_data close
        ticker_data['close '] = ticker_data["close"].astype(float)
        price = ([float(value) for value in ticker_data["close"].tolist()])
        
        labels = ([timestamp.strftime("%H:%M:%S") for timestamp in ticker_data.index])
        # ("%Y-%m-%d %H:%M:%S" Yearly Interval
        
        price_list = ticker_data["close"].tolist()
        stock_price = price_list[-1]
    
        
        opening_price = price_list[0]

        percent_change = ((stock_price - opening_price) / opening_price) * 100
        #
         
        return {"price": price, "labels": labels, "stock_price": stock_price, 'percentage': percent_change}      
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
    
        
        
    return sorted_score[:5]


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




def get_company_name(stock_ticker: str):
    try:
        profile = finnhub_client.company_profile2(symbol=stock_ticker.upper())
        return profile.get("name", stock_ticker.upper())
    except Exception as e:
        print(f"Error fetching company name: {e}")
        return stock_ticker.upper()