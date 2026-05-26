from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from ingestion.models import Tenant, Facility


class Command(BaseCommand):
    help = "Create demo user, tenant, and facilities for deployed demo"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "analyst@demo.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password("Demo@123")
            user.save()
            self.stdout.write(self.style.SUCCESS("Demo admin user created"))
        else:
            user.set_password("Demo@123")
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS("Demo admin user updated"))

        tenant, _ = Tenant.objects.get_or_create(
            slug="demo-client",
            defaults={"name": "Demo Enterprise Client"},
        )

        Facility.objects.get_or_create(
            tenant=tenant,
            code="BLR01",
            defaults={"name": "Bangalore Manufacturing Plant", "country": "India"},
        )

        Facility.objects.get_or_create(
            tenant=tenant,
            code="BLR02",
            defaults={"name": "Bangalore Office Campus", "country": "India"},
        )

        self.stdout.write(self.style.SUCCESS("Demo tenant and facilities ready"))