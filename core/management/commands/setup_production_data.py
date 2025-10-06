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

        # Create some sample employees for immediate testing
        self.stdout.write('\nCreating sample employees...')
        
        sample_employees = [
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

        for emp_data in sample_employees:
            # Create employee user
            employee, created = User.objects.get_or_create(
                username=emp_data['username'],
                defaults={
                    'email': emp_data['email'],
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            if created:
                employee.set_password('employee123')
                employee.save()
                self.stdout.write(f'Created employee: {employee.first_name} {employee.last_name}')
            
            # Update employee profile
            if hasattr(employee, 'profile'):
                profile = employee.profile
                profile.organization = org
                profile.phone = '+44123456780'
                profile.job_title = emp_data['job_title']
                profile.save()
            
            # Create employee membership
            emp_membership, created = OrgMembership.objects.get_or_create(
                user=employee,
                organization=org,
                defaults={'role': 'staff'}
            )
            
            if created:
                self.stdout.write(f'Created membership for: {employee.username}')

        self.stdout.write(self.style.SUCCESS('\n=== SETUP COMPLETE ==='))
        self.stdout.write(f'Organization: {org.name}')
        self.stdout.write(f'Admin username: {admin.username}')
        self.stdout.write(f'Admin email: {admin.email}')
        self.stdout.write(self.style.WARNING(f'Admin password: {options["admin_password"]}'))
        
        # Show available employees for ID cards
        self.stdout.write('\n=== AVAILABLE EMPLOYEES FOR ID CARDS ===')
        employees_count = User.objects.filter(org_memberships__organization=org).count()
        self.stdout.write(f'Total employees in organization: {employees_count}')
        
        for user in User.objects.filter(org_memberships__organization=org):
            job_title = getattr(user.profile, 'job_title', 'No job title') if hasattr(user, 'profile') else 'No profile'
            self.stdout.write(f'  - {user.first_name} {user.last_name} ({user.username}) - {job_title}')
        
        self.stdout.write(self.style.WARNING('\nIMPORTANT: Change the admin password after first login!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Login as admin')
        self.stdout.write('2. Go to ID Cards → Create New ID Card')
        self.stdout.write('3. Select from the available employees')
        self.stdout.write('4. Create additional employees through Admin → Users')
