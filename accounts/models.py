from django.db import models
from django.contrib.auth.models import User
import secrets

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_secret_key = models.CharField(max_length=64, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.user_secret_key:
            self.user_secret_key = secrets.token_hex(32)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile<{self.user_id}>"
