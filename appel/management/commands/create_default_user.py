from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create default user for testing'

    def handle(self, *args, **options):
        username = 'user1'
        password = '1234'
        email = 'user1@example.com'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
        else:
            User.objects.create_user(username=username, password=password, email=email)
            self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username}'))
