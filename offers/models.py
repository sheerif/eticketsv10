from django.db import models

class Offer(models.Model):
    SOLO, DUO, FAMILLE = "solo","duo","familiale"
    OFFER_TYPES = [(SOLO,"Solo"),(DUO,"Duo"),(FAMILLE,"Familiale")]
    name = models.CharField(max_length=100)
    offer_type = models.CharField(max_length=16, choices=OFFER_TYPES)
    description = models.TextField(blank=True)
    price_eur = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.offer_type})"
