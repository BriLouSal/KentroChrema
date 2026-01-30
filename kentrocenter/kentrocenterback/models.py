from django.db import models
from django.contrib.auth.models import User # The "ID Card"
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


# What do we want for our models: We'd want to grab the user's portfolio, so we can have like a portfolio list similar to my MarketSight Project.

# This project is much more models.py reliant, as we need our Snaptrade API
# We want to also auto-reg


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    # We wanna do a foreign key that holds SnapTrade Id for users
    # Null should be true because a user cannot automatically have an id as soon as they signup
    # We could change this via some conditional statement and auto resgistert
    snaptrade_user_id = models.CharField(max_length=255, null=True, blank=True)
    snaptrade_user_secret = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.username


"""sumary_line

Keyword arguments:
argument -- description
Return: return_description
"""
