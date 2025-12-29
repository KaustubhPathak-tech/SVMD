from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage  # ADD THIS LINE
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
    avatar = models.ImageField(
        upload_to="profile_images/", 
        blank=True, null=True,
        storage=MediaCloudinaryStorage()  # ADD THIS LINE
    )

    def __str__(self):
        return self.user.username

# class Photo(models.Model):
#     title = models.CharField(max_length=50)
#     image = models.ImageField(upload_to="photos/")
    
#     def __str__(self):
#         return self.title