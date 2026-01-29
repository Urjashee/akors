from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Role

class Command(BaseCommand):
    help = "Seed roles"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding lookup tables...")

        roles = ["Super admin", "Property manager", "Operator"]

        for model, values in [
            (Role, roles),
        ]:
            for name in values:
                model.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS("✅ Roles Seeding completed"))
