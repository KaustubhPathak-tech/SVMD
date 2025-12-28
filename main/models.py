from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from django.db import models

class EmailLoginToken(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=10)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='profile_images/', default='default.jpg')

    def __str__(self):
        return self.user.username


# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     else:
#         if hasattr(instance, 'profile'):
#             instance.profile.save()