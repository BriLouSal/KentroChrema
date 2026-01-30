from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail


# Create your views here.


# REFERENCE: https://docs.snaptrade.com/docs/getting-started
# https://pypi.org/project/snaptrade-python-sdk/



# Plans: First we need to have our signup/authentication systems ready at any cost,

# TOOO: Home should be a signup form!
def signup_page(request):
    # If the user is already logged in, we'll just put them redirect them to the portfolio setting.
    if request.user.is_authenticated:
        redirect('home')

    # Signup
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            redirect("signup")
        elif User.objects.filter(username=username).exists():
            redirect("signup")
        # Then we should redirect the user to verification code and match it email
        else:
            # We should also build a absoloute url for security purposes, 
            user = User.objects.create(username=username, password=password, email=email)
            user.is_authenticated(False)
            user.save()

            return redirect('verify')



    return render(request, 'base/signup.html')
# This will be our API call towards Google for users to login via this method



# Create a views where the user can enter their StockPortfolio signup to Wealthsimple, Shakepay, etc.

def verification_page(request):
    pass
def home(request):
    # We want this to be our portfolio view, but first we might wanna do is connect our API/investment platform!
    if request.user.is_authenticated:
        pass
    else: 
        redirect('signup')

def login(request):
    pass
