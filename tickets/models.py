from django.db import models
from django.contrib.auth.models import User
from offers.models import Offer
from orders.models import Order
import hashlib, qrcode
from django.conf import settings
from pathlib import Path

def checksum(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:8]

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT)
    ticket_key = models.CharField(
        max_length=128, 
        unique=True, 
        editable=False,
        db_index=True,  # Database index for fast lookups
        help_text="Unique ticket key with checksum for verification"
    )
    qr_image = models.ImageField(upload_to="qr/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Track creation time
    verified_at = models.DateTimeField(null=True, blank=True)  # Track verification

    class Meta:
        indexes = [
            models.Index(fields=['user', 'order'], name='tickets_user_order_idx'),
            models.Index(fields=['order', 'offer'], name='tickets_order_offer_idx'),
            models.Index(fields=['created_at'], name='tickets_created_at_idx'),
        ]
        ordering = ['-created_at']

    @classmethod
    def create_from(cls, user: User, order: Order, offer: Offer):
        base = user.profile.user_secret_key + order.purchase_key
        serial = cls.objects.filter(order=order).count() + 1
        raw = f"{base}-{serial}"
        key = f"{raw}:{checksum(raw)}"
        while cls.objects.filter(ticket_key=key).exists():
            serial += 1
            raw = f"{base}-{serial}"
            key = f"{raw}:{checksum(raw)}"

        t = cls.objects.create(user=user, order=order, offer=offer, ticket_key=key)
        img = qrcode.make(key)
        media = Path(settings.MEDIA_ROOT)
        media.mkdir(parents=True, exist_ok=True)
        path = media / f"qr/TCK-{t.id}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
        t.qr_image.name = str(path.relative_to(media))
        t.save()
        return t
