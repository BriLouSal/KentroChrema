import twelvedata
from datetime import date
from dateutil.relativedelta import relativedelta
from twelvedata import TDClient
from snaptrade_client import SnapTrade


from datetime import datetime

import finnhub

from django.http import HttpResponse, JsonResponse
from finnhub import Client
import os
from dotenv import load_dotenv
import ta
import pandas as pd
from yahooquery import Screener, Ticker


from asgiref.sync import sync_to_async, async_to_sync
import asyncio
from django.core.cache import cache


from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass, AssetStatus
from alpaca_trade_api import list_assets
import os 
from dotenv import load_dotenv



load_dotenv()



ALPACA = os.getenv('ALPACA')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

alpaca_client = TradingClient(api_key=ALPACA, secret_key=ALPACA_SECRET_KEY)


# We wanna create a fetch url, so that everytime the user inputs something from JS we'd fetch it and grab the stock data

@sync_to_async
def stock_engine_grab_data(data: str):

    data = data.upper()
    cache_key = f"autocomplete:{data}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    ASSET_CACHE_KEY = "alpaca_all_assets"
    assets = cache.get(ASSET_CACHE_KEY)

    if not assets:
        stock_params = GetAssetsRequest(
            status=AssetStatus.ACTIVE,
            asset_class=AssetClass.US_EQUITY,
        )
        assets = alpaca_client.get_all_assets(stock_params)
        cache.set(ASSET_CACHE_KEY, assets, 86400)

    TOP_EXCHANGE = {
        'NASDAQ': 0,
        'NYSE': 0,
    }

    FORBIDDEN_EXCHANGE = ['ARCA', 'OTC', 'BATS']


    stock_rec = [
        a for a in assets
        if a.symbol.upper().startswith(data)
        and a.tradable
        and a.exchange.value not in FORBIDDEN_EXCHANGE
    ][:80]

    def rank(asset):
        return (
            0 if asset.symbol == data else 1,
            len(asset.symbol),
            TOP_EXCHANGE.get(asset.exchange.value, 1)
        )

    stock_rec.sort(key=rank)

    result = [
        {
            "symbol": a.symbol,
            "name": a.name,
            "exchange": a.exchange.value,
        }
        for a in stock_rec[:11]
    ]

    cache.set(cache_key, result, 300)
    return result



    # return result



async def information_letter(request, letters):
    results = await stock_engine_grab_data(letters)
    return JsonResponse({'results': results})


def ticker_exists_database(stock_tick: str) -> bool:
    try:
        asset = alpaca_client.get_asset(stock_tick)
        if asset.tradable and asset.status == "active":
            return True
        else:
            return False
    # APi Error
    except Exception as e:
        print(f"Exception Raised: Error {e}")
        return None
    
    
    
