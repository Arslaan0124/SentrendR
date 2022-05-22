from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.shortcuts import get_object_or_404


#app imports from
from .constants import DEFAULT_USER_TIER
# Create your models here.




class UserTier(models.Model):

    tier_name = models.CharField(max_length=255,default="basic")
    max_keywords = models.IntegerField(default= 10)

    def __str__(self):
        return self.tier_name



class CustomUser(AbstractUser):

    email = models.EmailField(verbose_name='email address',max_length=255, unique=True)
    tier = models.ForeignKey(UserTier,null=True,on_delete=models.CASCADE)

    objects = CustomUserManager()

    def __str__(self):
        return self.email


    def get_tier(self):
        tier_obj,created = UserTier.objects.get_or_create(tier_name=DEFAULT_USER_TIER)
        tier_obj.save()
        return tier_obj

    def save(self, *args, **kwargs):
        self.tier = self.get_tier()
        super().save(*args, **kwargs)  # Call the "real" save() method.


