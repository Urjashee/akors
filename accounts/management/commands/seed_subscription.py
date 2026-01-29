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
                "external_id": None,
            },
            {
                "name": "Basic Plan",
                "amount": 49,
                "external_id": "price_basic_001",
            },
            {
                "name": "Premium Plan",
                "amount": 100,
                "external_id": "price_pro_001",
            },
            {
                "name": "Ultimate Plan",
                "amount": 150,
                "external_id": "price_ultimate_001",
            },
        ]

        for sub in subscriptions:
            Subscriptions.objects.get_or_create(
                name=sub["name"],
                defaults={
                    "amount": sub["amount"],
                    "external_id": sub["external_id"],
                },
            )

        self.stdout.write(self.style.SUCCESS("✅ Subscriptions seeded successfully"))
