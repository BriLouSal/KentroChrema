from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

# Create your views here.


# REFERENCE: https://docs.snaptrade.com/docs/getting-started
# https://pypi.org/project/snaptrade-python-sdk/



# Plans: First we need to have our login/authentication systems ready at any cost,

# TOOO: Home should be a login form!
def home(request):
    # If the user is already logged in, we'll just put them redirect them to the portfolio setting.
    return render(request, 'base/login.html')

# Create a views where the user can enter their StockPortfolio login to Wealthsimple, Shakepay, etc.


