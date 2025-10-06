# core/management/commands/add_employee.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile, OrgMembership
from core.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Add a new employee to an organization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Employee username'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Employee email'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            required=True,
            help='Employee first name'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            required=True,
            help='Employee last name'
        )
        parser.add_argument(
            '--job-title',
            type=str,
            default='Employee',
            help='Employee job title'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='+44123456789',
            help='Employee phone number'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='employee123',
            help='Employee password'
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

        # Create employee user
        employee, created = User.objects.get_or_create(
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
            employee.set_password(options['password'])
            employee.save()
            self.stdout.write(self.style.SUCCESS(f'Created employee: {employee.first_name} {employee.last_name}'))
        else:
            self.stdout.write(f'Employee already exists: {employee.username}')
        
        # Update employee profile
        if hasattr(employee, 'profile'):
            profile = employee.profile
            profile.organization = org
            profile.phone = options['phone']
            profile.job_title = options['job_title']
            profile.save()
            self.stdout.write('Updated employee profile')
        
        # Create employee membership
        membership, created = OrgMembership.objects.get_or_create(
            user=employee,
            organization=org,
            defaults={'role': 'staff'}
        )
        
        if created:
            self.stdout.write('Created organization membership')
        
        self.stdout.write(self.style.SUCCESS('\n=== EMPLOYEE ADDED ==='))
        self.stdout.write(f'Username: {employee.username}')
        self.stdout.write(f'Email: {employee.email}')
        self.stdout.write(f'Name: {employee.first_name} {employee.last_name}')
        self.stdout.write(f'Job Title: {options["job_title"]}')
        self.stdout.write(f'Organization: {org.name}')
        self.stdout.write(f'Password: {options["password"]}')
        
        # Check total employees available for ID cards
        employees_count = User.objects.filter(org_memberships__organization=org).count()
        self.stdout.write(f'\nTotal employees available for ID cards: {employees_count}')
