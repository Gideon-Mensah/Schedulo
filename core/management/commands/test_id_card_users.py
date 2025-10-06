# core/management/commands/test_id_card_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import OrgMembership
from core.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Test which users would appear in ID card dropdown'

    def handle(self, *args, **options):
        self.stdout.write('=== TESTING ID CARD USER DROPDOWN ===')
        
        # Get organization
        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization found'))
            return
            
        self.stdout.write(f'Organization: {org.name}')
        
        # Test the exact query used in the form (updated to match shift booking system)
        queryset = User.objects.filter(
            profile__organization=org
        ).order_by('first_name', 'last_name')
        
        self.stdout.write(f'Query: User.objects.filter(profile__organization=org).order_by("first_name", "last_name")')
        self.stdout.write(f'Count: {queryset.count()}')
        
        if queryset.count() == 0:
            self.stdout.write(self.style.ERROR('No users found! Checking profiles...'))
            
            # Check profiles
            from accounts.models import Profile
            profiles = Profile.objects.filter(organization=org)
            self.stdout.write(f'Profiles for {org.name}: {profiles.count()}')
            for profile in profiles:
                self.stdout.write(f'  - {profile.user.username} -> {profile.organization.name}')
        else:
            self.stdout.write(self.style.SUCCESS('Users that would appear in dropdown:'))
            for user in queryset:
                self.stdout.write(f'  - {user.first_name} {user.last_name} ({user.username})')
        
        # Also test the old query for comparison
        self.stdout.write('\n=== OLD QUERY COMPARISON ===')
        old_queryset = User.objects.filter(org_memberships__organization=org).distinct()
        self.stdout.write(f'Old query (org_memberships): {old_queryset.count()} users')
        self.stdout.write(f'New query (profile__organization): {queryset.count()} users')
        
        # Also test if we can access these users directly
        self.stdout.write('\n=== ALL USERS WITH DETAILS ===')
        for user in User.objects.all():
            memberships = OrgMembership.objects.filter(user=user)
            self.stdout.write(f'User: {user.username}')
            self.stdout.write(f'  Memberships: {memberships.count()}')
            for m in memberships:
                self.stdout.write(f'    - {m.organization.name} ({m.role})')
