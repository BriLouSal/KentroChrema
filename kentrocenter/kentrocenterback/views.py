from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

# Create your views here.



# Plans: First we need to have our login/authentication systems ready at any cost,

# TOOO: Home should be a login form!
def home(request):
    pass