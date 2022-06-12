
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_delete,post_save
from .models import Trend

from django.db import transaction




@transaction.atomic
@receiver(pre_delete, sender=Trend)
def pre_delete_tweet(sender, instance, **kwargs):
    for tweet in instance.tweets.all():
        if tweet.trend.count() == 1:
            # instance is the only Entry authored by this Trend, so delete it
            tweet.delete()