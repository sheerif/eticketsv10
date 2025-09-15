from django.db import models
from django.contrib.auth.models import User
from offers.models import Offer
import secrets

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    purchase_key = models.CharField(max_length=32, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.purchase_key:
            self.purchase_key = secrets.token_hex(16)
        return super().save(*args, **kwargs)

    def total_eur(self):
        return sum(item.total_eur() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    def total_eur(self):
        return float(self.offer.price_eur) * self.quantity
