from django.db import models

class Province(models.Model):
    name = models.CharField(max_length=20, unique=True)

class City(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)

class User(models.Model):  # Django 기본 User 안 씀(대회 모드)
    username = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    avatar_url = models.URLField(blank=True)
    gender = models.CharField(max_length=10, blank=True)     # 'male'/'female'/'other'
    age_band = models.CharField(max_length=10, blank=True)   # '10s','20s',...
    intro = models.TextField(blank=True)
    manner_temperature = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
