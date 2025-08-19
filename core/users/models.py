from django.db import models

class User(models.Model):
    username = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    province_name = models.CharField(max_length=20, blank=True)
    city_name = models.CharField(max_length=40, blank=True)

    avatar_url = models.URLField(blank=True)
    gender = models.CharField(max_length=10, blank=True)     # 'male'/'female'/'other'
    age_band = models.CharField(max_length=10, blank=True)   # '10s','20s',...
    intro = models.TextField(blank=True)
    manner_temperature = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
