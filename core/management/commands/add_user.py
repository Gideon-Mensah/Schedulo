# core/management/commands/add_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile, OrgMembership
from core.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Add a new user to an organization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='User username'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='User email'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            required=True,
            help='User first name'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            required=True,
            help='User last name'
        )
        parser.add_argument(
            '--job-title',
            type=str,
            default='User',
            help='User job title'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='+44123456789',
            help='User phone number'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='user123',
            help='User password'
        )
        parser.add_argument(
            '--org-name',
            type=str,
            default='Delaala Company Limited',
            help='Organization name'
        )

    def handle(self, *args, **options):
        try:
            # Get organization
            org = Organization.objects.get(name=options['org_name'])
            self.stdout.write(f'Found organization: {org.name}')
        except Organization.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Organization "{options["org_name"]}" not found'))
            self.stdout.write('Available organizations:')
            for org in Organization.objects.all():
                self.stdout.write(f'  - {org.name}')
            return

        # Create user
        user, created = User.objects.get_or_create(
            username=options['username'],
            defaults={
                'email': options['email'],
                'first_name': options['first_name'],
                'last_name': options['last_name'],
                'is_staff': False,
                'is_superuser': False
            }
        )
        
        if created:
            user.set_password(options['password'])
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.first_name} {user.last_name}'))
        else:
            self.stdout.write(f'User already exists: {user.username}')
        
        # Update user profile
        if hasattr(user, 'profile'):
            profile = user.profile
            profile.organization = org
            profile.phone = options['phone']
            profile.job_title = options['job_title']
            profile.save()
            self.stdout.write('Updated user profile')
        
        # Create user membership
        membership, created = OrgMembership.objects.get_or_create(
            user=user,
            organization=org,
            defaults={'role': 'staff'}
        )
        
        if created:
            self.stdout.write('Created organization membership')
        
        self.stdout.write(self.style.SUCCESS('\n=== USER ADDED ==='))
        self.stdout.write(f'Username: {user.username}')
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Name: {user.first_name} {user.last_name}')
        self.stdout.write(f'Job Title: {options["job_title"]}')
        self.stdout.write(f'Organization: {org.name}')
        self.stdout.write(f'Password: {options["password"]}')
        
        # Check total users available for ID cards
        users_count = User.objects.filter(org_memberships__organization=org).count()
        self.stdout.write(f'\nTotal users available for ID cards: {users_count}')
