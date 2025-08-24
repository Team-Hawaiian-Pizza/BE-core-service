from django.db import models

class User(models.Model):
    username = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    province_name = models.CharField(max_length=20, blank=True)
    city_name = models.CharField(max_length=40, blank=True)

    # default=list는 새로운 사용자가 생성될 때 기본값으로 빈 리스트([])를 갖도록 합니다.
    tags = models.JSONField(default=list, blank=True)
    avatar_url = models.URLField(blank=True)
    profile_s3_key = models.CharField(max_length=500, blank=True)  # S3 object key for profile image
    gender = models.CharField(max_length=10, blank=True)     # 'male'/'female'/'other'
    age_band = models.CharField(max_length=10, blank=True)   # '10s','20s',...
    intro = models.TextField(blank=True)
    manner_temperature = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
