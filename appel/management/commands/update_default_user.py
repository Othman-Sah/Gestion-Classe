from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or update default user with specified credentials'

    def handle(self, *args, **options):
        # Delete old user1 if exists
        User.objects.filter(username='user1').delete()
        
        # Create new user with updated credentials
        user = User.objects.create_user(
            username='user',
            password='user1234',
            email='user@example.com'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created user: {user.username}\n'
                f'Password: user1234\n'
                f'Email: {user.email}'
            )
        )
