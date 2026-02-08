from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from .models import EmailVerificationCode, Profile
from django.core.mail import send_mail
from random import randint
from django.conf import settings
# Create your views here.

# from snaptrade import dk


# REFERENCE: https://docs.snaptrade.com/docs/getting-started
# https://pypi.org/project/snaptrade-python-sdk/



# Plans: First we need to have our signup/authentication systems ready at any cost,

# TOOO: Home should be a signup form!



def signup_page(request):
    # If the user is already logged in, we'll just put them redirect them to the portfolio setting.
    if request.user.is_authenticated:
        return redirect('home')

    # Signup
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            return redirect("verify")
        elif User.objects.filter(username=username).exists():
            return redirect("verify")
        # Then we should redirect the user to verification code and match it email
        else:
            # We should also build an absoloute url for security purposes, 
            user = User.objects.create_user(username=username, password=password, email=email)
            # They're not verified, and they'll have to do it through the built in url
            user.is_active = False
            user.save()

            profile = Profile.objects.create(
                user=user,
                is_verified=False
            )
            if user and user.is_active:
                return redirect("login")


            # So we wanna generate the verification code
            generated_code = str(randint(100000, 999999))
            # After that we wanna create the model of email verification and we can do a if-statement to check if the email verification is matched with the user
            EmailVerificationCode.objects.update_or_create(user=user, defaults={'code': generated_code, 'is_verified': False})

            request.session['verify_user_id'] = user.id

            send_mail(
                subject="Verify your code",
                message=f"Hello {username}, your verification code is {generated_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('verify')



    return render(request, 'base/signup.html')
# This will be our API call towards Google for users to login via this method



# Create a views where the user can enter their StockPortfolio signup to Wealthsimple, Shakepay, etc.

def verification_page(request):
    # This is where we'll send the verification code
    # and we also need the verification code here to match with user's connected email.
    code = request.POST.get('code')
    if request.method == 'POST':
        try:
            verification = EmailVerificationCode.objects.get(code=code)
            user = verification.user
            user.save()
            # Then log them in
            verification.delete()
            login(request, user)
            return redirect('home')
        # Signup would be required as if someone tried to do a url /verification/ it would have a messages.error


        except EmailVerificationCode.DoesNotExist:
            messages.error(request, "Verification Code does not Exist, Please Signup")
            return redirect('signup')
    return render(request, 'base/verification.html')
    
def home(request):
    # We want this to be our portfolio view, but first we might wanna do is connect our API/investment platform!
    if not request.user.is_authenticated:
        return redirect('signup')
    if not request.user.profile.is_verified:
        return redirect('verify')



    


def loginpage(request):
    if request.method == "POST":
        # This is how we'll login right

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password) 
        if user is None:
            messages.error(request, "This user does not exist, please signup or try again!")
            return redirect('login')
        login(request, user)
        if not request.user.is_authenticated or request.user.is_active:
            return redirect('signup')

        return redirect('home')
        
    return render(request, 'base/login.html')
