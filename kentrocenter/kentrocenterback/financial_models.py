#  This is for the financial item model, which will be used to store the financial items for the users., and we're also looking at sentiments from the insider
import twelvedata
from datetime import date
from dateutil.relativedelta import relativedelta
from twelvedata import TDClient
import finnhub
from finnhub import Client
import os
from dotenv import load_dotenv



load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

FINNHUB_API = os.getenv('FINNHUB_KEY')

API_KEY = os.getenv('ALPACA')
ALPACA_SECRET_KEY  = os.getenv('ALPACA_SECRET_KEY')
TWELVEDATA_API_KEY = os.getenv('TWELVEDATAAPI')


finnhub_client = Client(api_key=FINNHUB_API)

TWELVEDATA_API_KEY = os.getenv('TWELVEDATAAPI')



def insider_transaction_trading(stock_ticker: str,):
    """sumary_line
    
    Keyword arguments:
    argument -- Stock ticker symbol (e.g., "AAPL" for Apple Inc.)
    Return: it will return a list of dictionaries containing insider trading information, including the insider's name, relationship to the company, transaction date, transaction type, number of shares traded, and share price.
    """
    
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



def stockData(stock_ticker: str):
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

        price = ([float(value) for value in ticker_data["close"].tolist()])
        
        labels = ([timestamp.strftime("%Y-%m-%d %H:%M:%S") for timestamp in ticker_data.index])
        
        print("Price data:", price)
        print("Labels data:", labels)
    

     
     
        return {"price": price, "labels": labels}
        
        
            
        
        # Now we have to parse the data and grab the price and the date, and we'll have to reverse it as well so that we can have the most recent data at the end of the list, which will be used for Chart.JS\  



    except Exception as e:
        print(f"Error fetching stock data for {stock_ticker}: {e}")
        return None  # Return None or an appropriate value to indicate failure
        