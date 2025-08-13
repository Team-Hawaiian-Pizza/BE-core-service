from django.db import models

class InviteCode(models.Model):
    owner = models.OneToOneField('users.User', on_delete=models.CASCADE)
    code  = models.CharField(max_length=12, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

class ConnectionRequest(models.Model):
    PENDING="PENDING"; ACCEPTED="ACCEPTED"; REJECTED="REJECTED"
    from_user = models.ForeignKey('users.User', related_name='conn_from', on_delete=models.CASCADE)
    to_user   = models.ForeignKey('users.User', related_name='conn_to',   on_delete=models.CASCADE)
    via_friend= models.ForeignKey('users.User', null=True, blank=True, related_name='conn_via', on_delete=models.SET_NULL)
    status    = models.CharField(max_length=10, default=PENDING)
    created_at= models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["to_user","status"])]
