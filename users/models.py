from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=10)
    email = models.EmailField("이메일", blank=True, null=True)
    profile_image = models.ImageField("프로필 이미지", upload_to='user/profile', blank=True, null=True)
    joined_at = models.DateTimeField("가입일", auto_now_add=True)

    def __str__(self):
        return self.username