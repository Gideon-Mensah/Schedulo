# core/management/commands/setup_production_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile, OrgMembership
from core.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial production data for Schedulo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--org-name',
            type=str,
            default='Delaala Company Limited',
            help='Organization name to create'
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Admin username'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@delaala.co.uk',
            help='Admin email'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='ChangeMe123!',
            help='Admin password (please change after first login)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up production data...'))
        
        # Create organization
        org, created = Organization.objects.get_or_create(
            name=options['org_name'],
            defaults={
                'email_sender': f'noreply@{options["org_name"].lower().replace(" ", "")}.co.uk',
                'email_display_name': options['org_name']
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created organization: {org.name}'))
        else:
            self.stdout.write(f'Organization already exists: {org.name}')

        # Create admin user
        admin, created = User.objects.get_or_create(
            username=options['admin_username'],
            defaults={
                'email': options['admin_email'],
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin.set_password(options['admin_password'])
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))
            self.stdout.write(self.style.WARNING(f'Admin password: {options["admin_password"]} - PLEASE CHANGE AFTER FIRST LOGIN!'))
        else:
            self.stdout.write(f'Admin user already exists: {admin.username}')

        # Update admin profile
        if hasattr(admin, 'profile'):
            profile = admin.profile
            profile.organization = org
            profile.phone = '+44123456789'
            profile.job_title = 'System Administrator'
            profile.save()
            self.stdout.write('Updated admin profile')

        # Create admin membership
        membership, created = OrgMembership.objects.get_or_create(
            user=admin,
            organization=org,
            defaults={'role': 'owner'}
        )
        
        if created:
            self.stdout.write('Created admin organization membership')

        self.stdout.write(self.style.SUCCESS('\n=== SETUP COMPLETE ==='))
        self.stdout.write(f'Organization: {org.name}')
        self.stdout.write(f'Admin username: {admin.username}')
        self.stdout.write(f'Admin email: {admin.email}')
        self.stdout.write(self.style.WARNING(f'Admin password: {options["admin_password"]}'))
        self.stdout.write(self.style.WARNING('IMPORTANT: Change the admin password after first login!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Login as admin')
        self.stdout.write('2. Create employee users through the admin interface')
        self.stdout.write('3. Create ID cards for employees')
