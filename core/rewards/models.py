from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=80)
    hero_image = models.TextField(blank=True)
    benefit_text = models.CharField(max_length=120, blank=True)

class StampBoard(models.Model):
    user  = models.ForeignKey('users.User', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    total = models.PositiveIntegerField(default=10)
    filled= models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user','brand')

class Coupon(models.Model):
    user  = models.ForeignKey('users.User', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    image = models.URLField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
