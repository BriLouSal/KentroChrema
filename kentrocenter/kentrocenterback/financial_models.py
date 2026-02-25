#  This is for the financial item model, which will be used to store the financial items for the users., and we're also looking at sentiments from the insider
import twelvedata
from datetime import date
from dateutil.relativedelta import relativedelta
from twelvedata import TDClient
import finnhub
from finnhub import Client
import os
from dotenv import load_dotenv
import ta
import pandas as pd
from .KOSAI import secret_indicator

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

FINNHUB_API = os.getenv('FINNHUB_KEY')

API_KEY = os.getenv('ALPACA')
ALPACA_SECRET_KEY  = os.getenv('ALPACA_SECRET_KEY')
TWELVEDATA_API_KEY = os.getenv('TWELVEDATAAPI')


finnhub_client = Client(api_key=FINNHUB_API)



def bullish_indicator(stock_ticker: str, years=1, interval='1d'):
    # This is for the bullish indicator, which will be used to determine if the stock is bullish or bearish based on the insider trading information, and we'll use the sentiment analysis from the insider trading information to determine if the stock is bullish or bearish.
    stock_ticker = stock_ticker.upper()
    twelvedata_client = TDClient(apikey=TWELVEDATA_API_KEY)
    
    
    points = 0
    
    try:
        stock_price = twelvedata_client.time_series(
            symbol=stock_ticker,
            interval=interval,
            start_date=(date.today() - relativedelta(years=years)).strftime('%Y-%m-%d'),
            
            outputsize=100
        ).as_pandas()
        
        
        close_price = stock_price["close"].astype(float)
        # You don't have to rename the columns, you can just use the original column names, and you can also use the original index as the date, which will be easier for us to use with Chart.JS.
        
        stock_price = stock_price.iloc[::-1]
        stock_price["close"] = stock_price["close"].astype(float)
        
        rsi_indicaator = ta.momentum.RSIIndicator(stock_price["close"], window=14)
        
        stock_price["RSI"] = rsi_indicaator.rsi()
        
        
        # For our RSI strength

        # RSI Range & Key Levels
        # 0 to 100: The fundamental range for the RSI oscillator.
        # Overbought: Above 70 (or 80/90).
        # Oversold: Below 30 (or 20/10).
        # Neutral Zone: Between 30 and 70. 

        # if Oversold it should be higher score, as it's a great sign for a breakout:

        # Use RSI_14 MODEL (14-day average)
        if stock_price["RSI"].iloc[-1] < 30:
            points += 20  # Oversold, potential bullish signal
        elif stock_price["RSI"].iloc[-1] > 70:
            points -= 20  # Overbought, potential bearish signal
        else:
            points += 0  # Neutral, no change to points
            
        # now find the Bollinger Bands
        bollinger_indicator = ta.volatility.BollingerBands(stock_price["close"], window=20, window_dev=2)
        stock_price["bb_bbh"] = bollinger_indicator.bollinger_hband()
        stock_price["bb_bbl"] = bollinger_indicator.bollinger_lband()
        stock_price["bb_bbm"] = bollinger_indicator.bollinger_mavg()
        
        # And use that to find the bandwidth, which is the distance between the upper and lower bands, and use that to determine if the stock is volatile or not.
        
        
    # Volatility: Bollinger Bonds. 
    # Important formula (The Bollinger Bandwidth Formula): \(\text{BBW}=\frac{\text{Upper\ Band}-\text{Lower\ Band}}{\text{Middle\ Band}}\)
    # So grab the Upper, Lower, and Middle band, and then use the formula to find the bandwidth, which will be used to determine if the stock is volatile or not.z
        stock_price["Bollinger_Bandwidth"] = (stock_price["bb_bbh"] - stock_price["bb_bbl"]) / stock_price["bb_bbm"]
        
       
       
        # Now we compare, if the bollinger bandwidth is high, it means that the stock is volatile, and if the price is above the upper band, it means that the stock is overbought, and if the price is below the lower band, it means that the stock is oversold.
        if stock_price["close"].iloc[-1] > stock_price["bb_bbh"].iloc[-1]:
            points += 12  # Price above upper band, potential bullish signal
        elif stock_price["close"].iloc[-1] > stock_price["bb_bbm"].iloc[-1]:
            points += 8  # Price above middle band, potential bullish signal
        
        elif stock_price["close"].iloc[-1] < stock_price["bb_bbm"].iloc[-1] and stock_price["close"].iloc[-1] >= stock_price["bb_bbl"].iloc[-1]:
            points += 0  # Price between middle and lower band, neutral signal
        elif stock_price["close"].iloc[-1] < stock_price["bb_bbl"].iloc[-1]:
            points -= 5  # Price below lower band, potential bearish signal
            
        # Let's find the SMA
        fifty_sma_average = ta.trend.SMAIndicator(stock_price["close"], window=50)
        two_hundred_sma_average = ta.trend.SMAIndicator(stock_price["close"], window=200)
        stock_price["SMA_50"] = fifty_sma_average.sma_indicator()
        stock_price["SMA_200"] = two_hundred_sma_average.sma_indicator()
        # If the price is above the 50 SMA, it's a bullish signal, and if it's below, it's a bearish signal.
        if stock_price["close"].iloc[-1] > stock_price["SMA_50"].iloc[-1]:
            points += 10  # Price above 50 SMA, potential bullish signal
        else:
            points -= 10  # Price below 50 SMA, potential bearish signal
        
        
        # Now we put our secret indicator
        
        points += secret_indicator(years)
        
        
        
        return max(min(points, 100), 0)  # Ensure points are not over 100

        
    except Exception as e:
        print(f"Error fetching stock price data for {stock_ticker}: {e}")
        return None  # Return None or an appropriate value to indicate failure
    
def risk_models(stock_ticker: str):
    # This is for the risk models, which will be used to determine the risk of the stock based on the insider trading information, and we'll use the sentiment analysis from the insider trading information to determine if the stock is risky or not.
    stock_ticker = stock_ticker.upper()
    twelvedata_client = TDClient(apikey=TWELVEDATA_API_KEY)
    
    try:
        stock_price = twelvedata_client.time_series(
            symbol=stock_ticker,
            interval="1min",
            outputsize=100
        ).as_pandas()
        # You don't have to rename the columns, you can just use the original column names, and you can also use the original index as the date, which will be easier for us to use with Chart.JS.
        
        stock_price = stock_price.iloc[::-1]
        stock_price["close"] = stock_price["close"].astype(float)
        volatility_indicator = ta.volatility.AverageTrueRange(stock_price["high"], stock_price["low"], stock_price["close"], window=14)
        stock_price["ATR"] = volatility_indicator.average_true_range()
        
        
        
        
    except Exception as e:
        print(f"Error fetching stock price data for {stock_ticker}: {e}")
        return None  # Return None or an appropriate value to indicate failure