import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create the initial superuser when explicitly enabled by environment variables.'

    def handle(self, *args, **options):
        if os.environ.get('BOOTSTRAP_SUPERUSER', '').strip().lower() != 'true':
            self.stdout.write('Superuser bootstrap is disabled.')
            return

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
        missing = [
            name
            for name, value in (
                ('DJANGO_SUPERUSER_USERNAME', username),
                ('DJANGO_SUPERUSER_EMAIL', email),
                ('DJANGO_SUPERUSER_PASSWORD', password),
            )
            if not value
        ]
        if missing:
            raise CommandError(
                'Set the required Render environment variables: ' + ', '.join(missing)
            )

        User = get_user_model()
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if existing_user.email and existing_user.email.casefold() != email.casefold():
                raise CommandError(
                    f'Username {username!r} is already linked to a different email address.'
                )
            existing_user.email = email
            existing_user.is_active = True
            existing_user.is_staff = True
            existing_user.is_superuser = True
            existing_user.set_password(password)
            existing_user.save(update_fields=[
                'email', 'is_active', 'is_staff', 'is_superuser', 'password',
            ])
            self.stdout.write(self.style.SUCCESS(
                f'Superuser {username!r} is ready; password updated from the protected environment value.'
            ))
            return

        User._default_manager.db_manager().create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser {username!r} created.'))
