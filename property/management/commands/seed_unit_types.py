from django.core.management.base import BaseCommand
from django.db import transaction

from property.models import UnitType


class Command(BaseCommand):
    help = "Seed unit classes"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding lookup tables...")

        items = ["Elevator",
                  "Escalator",
                  "Miscellaneous"]

        for model, values in [
            (UnitType, items),
        ]:
            for name in values:
                model.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS("✅ Unit Types Seeding completed"))
