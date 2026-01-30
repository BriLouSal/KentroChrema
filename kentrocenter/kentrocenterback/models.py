from django.db import models
from django.contrib.auth.models import User # The "ID Card"
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


# What do we want for our models: We'd want to grab the user's portfolio, so we can have like a portfolio list similar to my MarketSight Project.



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)