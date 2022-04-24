from django.db import models

# Keeps track of a user's balance
class Balances(models.Model):
    key = models.CharField(max_length=66, blank=False, null=False, unique=True, db_index=True)
    pending = models.IntegerField()
    available = models.IntegerField()
    withdrawn = models.IntegerField()

# Keeps track of sent tweets
class Tweet(models.Model):
    key = models.CharField(max_length=66, blank=False, null=False, db_index=True)
    twitter_id = models.CharField(max_length=25, blank=False, null=False, unique=True)
    created = models.DateTimeField(auto_now=True)
    stake = models.IntegerField(default=100)
    invoice_id = models.CharField(max_length=100, blank=False)