from django.db import models


class Balances(models.Model):
    key = models.CharField(max_length=66, blank=False, null=False, unique=True, db_index=True)
    pending = models.IntegerField()
    available = models.IntegerField()
    withdrawn = models.IntegerField()

class Tweet(models.Model):
    key = models.CharField(max_length=66, blank=False, null=False, unique=True, db_index=True)
    twitter_id = models.CharField(max_length=25, blank=False, null=False, unique=True)
    created = models.DateTimeField(auto_now=True)
    stake = models.IntegerField(default=100)
    invoice_id = models.CharField(max_length=100, blank=False)