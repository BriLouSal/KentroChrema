from django.db import models

# Create your models here.


# What do we want for our models: We'd want to grab the user's portfolio, so we can have like a portfolio list similar to my MarketSight Project.



class Profile(models.Model):
    username = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    password = models.CharField(max_length=100)
    created = models.DateField(auto_now_add=True)
    # 
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

