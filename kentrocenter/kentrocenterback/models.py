from django.db import models
from django.contrib.auth.models import User # The "ID Card"
from django.db.models.signals import post_save

from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
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
        return self.user.username or self.user.email



class EmailVerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 6 digits
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
    def __str__(self):
        return f"{self.user.email} - {self.code}"

class BrokerageAccount(models.Model):
    account  = models.ForeignKey(User, on_delete=models.CASCADE)
    snaptrade_user_id = models.CharField(max_length=255)
    snaptrade_user_secret = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
# Data needed: Book Cost, User, Avg_cost, SharesHold,  market_value, value_of_stock
class Holding(models.Model):
    user = models.ForeignKey(BrokerageAccount, on_delete=models.CASCADE)
    book_cost = models.FloatField()
    # Shareshold must be float to consider partial shares
    shares_hold = models.FloatField()
    market_value = models.FloatField()
    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Using the mistake from MarketSight, we'd want to create a portfolio date_time

class PortfolioTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="snapshots")
    total_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["created_at"]