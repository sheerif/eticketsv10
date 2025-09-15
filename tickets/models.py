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
    ticket_key = models.CharField(max_length=128, unique=True, editable=False)
    qr_image = models.ImageField(upload_to="qr/", blank=True, null=True)

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
