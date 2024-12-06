from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from config import settings


class Command(BaseCommand):
    help = "Automatically creates a superuser"

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                "admin",
                settings.DJANGO_SUPERUSER_EMAIL,
                settings.DJANGO_SUPERUSER_PASSWORD,
            )
            self.stdout.write(self.style.SUCCESS("Superuser created successfully"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists"))
