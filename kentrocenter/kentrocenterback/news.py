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
            "sentiment_score": round(sentiment_stock_score.polarity_scores(headline)["compound"], 2),
            "impact_score": abs(sentiment_stock_score.polarity_scores(headline)["compound"]),
            "source": news["source"]
            
        })
    sorted_stock_news = sorted(
        stock_news_data,
        key=lambda x: abs(x["sentiment_score"]),
        reverse=True,
    )
    return sorted_stock_news[:5]




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
