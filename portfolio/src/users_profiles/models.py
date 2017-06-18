from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import UserAddress


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, null=True, blank=True)
    surname = models.CharField(max_length=120, null=True, blank=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    default_billing_address = models.ForeignKey(UserAddress, null=True, blank=True,
                                                related_name='default_billing_address')
    default_shipping_address = models.ForeignKey(UserAddress, null=True, blank=True,
                                                 related_name='default_shipping_address')

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created or not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.userprofile:
        instance.userprofile.save()  # or user_profile
