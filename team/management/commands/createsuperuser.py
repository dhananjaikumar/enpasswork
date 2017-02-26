from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username="vinod").exists():
            User.objects.create_superuser("vinod", "vinod@sinew.in", "qwerty12345")
