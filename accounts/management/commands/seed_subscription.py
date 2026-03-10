from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Subscriptions


class Command(BaseCommand):
    help = "Seed subscriptions"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding subscriptions...")

        subscriptions = [
            {
                "name": "Operator Plan",
                "amount": 5,
                "external_id": "price_1T504UBDnPGPFOY8VTUSq0Wc",
                "units": 10000000
            },
            {
                "name": "Basic Plan",
                "amount": 49,
                "external_id": "price_1T4zyCBDnPGPFOY8gl9kKiXX",
                "units": 10
            },
            {
                "name": "Premium Plan",
                "amount": 100,
                "external_id": "price_1T501NBDnPGPFOY8rZQD6HoW",
                "units": 25
            },
            {
                "name": "Ultimate Plan",
                "amount": 150,
                "external_id": "price_1T5031BDnPGPFOY86b37xTf5",
                "units": 10000000
            },
        ]

        for sub in subscriptions:
            Subscriptions.objects.update_or_create(
                name=sub["name"],
                defaults={
                    "amount": sub["amount"],
                    "external_id": sub["external_id"],
                    "units": sub["units"],
                },
            )

        self.stdout.write(self.style.SUCCESS("✅ Subscriptions seeded successfully"))
