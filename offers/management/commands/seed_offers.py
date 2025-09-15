from django.core.management.base import BaseCommand
from offers.models import Offer

DEFAULTS = [
    dict(name="Solo", offer_type="solo", price_eur=50, is_active=True),
    dict(name="Duo", offer_type="duo", price_eur=90, is_active=True),
    dict(name="Familiale", offer_type="familiale", price_eur=150, is_active=True),
]

class Command(BaseCommand):
    help = "Seed default offers"

    def handle(self, *args, **kwargs):
        created = 0
        for d in DEFAULTS:
            obj, was_created = Offer.objects.get_or_create(name=d["name"], defaults=d)
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Seeded offers. New: {created}"))
