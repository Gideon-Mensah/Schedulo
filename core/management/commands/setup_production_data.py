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

        # Create some sample users for immediate testing
        self.stdout.write('\nCreating sample users...')
        
        sample_users = [
            {
                'username': 'john.doe',
                'email': 'john.doe@delaala.co.uk',
                'first_name': 'John',
                'last_name': 'Doe',
                'job_title': 'Software Developer'
            },
            {
                'username': 'jane.smith', 
                'email': 'jane.smith@delaala.co.uk',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'job_title': 'Marketing Manager'
            }
        ]

        for user_data in sample_users:
            # Create user
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            if created:
                user.set_password('user123')
                user.save()
                self.stdout.write(f'Created user: {user.first_name} {user.last_name}')
            
            # Update user profile
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.organization = org
                profile.phone = '+44123456780'
                profile.job_title = user_data['job_title']
                profile.save()
            
            # Create user membership
            user_membership, created = OrgMembership.objects.get_or_create(
                user=user,
                organization=org,
                defaults={'role': 'staff'}
            )
            
            if created:
                self.stdout.write(f'Created membership for: {user.username}')

        self.stdout.write(self.style.SUCCESS('\n=== SETUP COMPLETE ==='))
        self.stdout.write(f'Organization: {org.name}')
        self.stdout.write(f'Admin username: {admin.username}')
        self.stdout.write(f'Admin email: {admin.email}')
        self.stdout.write(self.style.WARNING(f'Admin password: {options["admin_password"]}'))
        
        # Show available users for ID cards
        self.stdout.write('\n=== AVAILABLE USERS FOR ID CARDS ===')
        users_count = User.objects.filter(org_memberships__organization=org).count()
        self.stdout.write(f'Total users in organization: {users_count}')
        
        for user in User.objects.filter(org_memberships__organization=org):
            job_title = getattr(user.profile, 'job_title', 'No job title') if hasattr(user, 'profile') else 'No profile'
            self.stdout.write(f'  - {user.first_name} {user.last_name} ({user.username}) - {job_title}')
        
        self.stdout.write(self.style.WARNING('\nIMPORTANT: Change the admin password after first login!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Login as admin')
        self.stdout.write('2. Go to ID Cards → Create New ID Card')
        self.stdout.write('3. Select from the available users')
        self.stdout.write('4. Create additional users through Admin → Users')
