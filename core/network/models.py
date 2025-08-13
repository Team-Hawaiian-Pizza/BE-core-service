from django.db import models

class Friendship(models.Model):
    a = models.ForeignKey('users.User', related_name='edges_out', on_delete=models.CASCADE)
    b = models.ForeignKey('users.User', related_name='edges_in',  on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('a','b')  # 중복 방지
