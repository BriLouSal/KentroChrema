from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

# Create your views here.


# REFERENCE: https://docs.snaptrade.com/docs/getting-started
# https://pypi.org/project/snaptrade-python-sdk/



# Plans: First we need to have our login/authentication systems ready at any cost,

# TOOO: Home should be a login form!
def login(request):
    # If the user is already logged in, we'll just put them redirect them to the portfolio setting.
    if request.user.is_authenticated:
        redirect('home')

    # Signup
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            redirect("login")
        elif User.objects.filter(username=username).exists():
            redirect("login")
        # Then we should redirect the user to verification code and match it
        else:
            user = User.objects.create(username=username, password=password, email=email)
            user.is_authenticated(False)
            redirect('verify')



    return render(request, 'base/login.html')



# Create a views where the user can enter their StockPortfolio login to Wealthsimple, Shakepay, etc.

def verification_page(request):
    pass
def home(request):
    pass