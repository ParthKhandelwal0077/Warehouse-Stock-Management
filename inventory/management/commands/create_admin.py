from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Create a superuser account'

    def handle(self, *args, **options):
        # Get admin credentials from environment variables or use defaults
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@warehouse.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

        # Check if admin user already exists
        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{admin_username}" already exists')
            )
            return

        # Create the admin user
        try:
            user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: {admin_username}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            ) 