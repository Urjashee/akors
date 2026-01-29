from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Title


class Command(BaseCommand):
    help = "Seed titles"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding lookup tables...")

        data = ["TPQEI Elevator inspector", "Elevator mechanic",
                  "Fire alarm tech", "Generator tech",
                  "Building personnel", "AHJ",
                  "Miscellaneous"]

        for model, values in [
            (Title, data),
        ]:
            for name in values:
                model.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS("✅ Roles Seeding completed"))
