from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from core.models import Organization, Domain


class Command(BaseCommand):
    help = 'Set up a new tenant organization with custom domain'

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True, help='Organization name')
        parser.add_argument('--domain', required=True, help='Custom domain (e.g., delaala.co.uk)')
        parser.add_argument('--email', help='Custom email sender for the organization')
        parser.add_argument('--display-name', help='Custom display name for emails')

    def handle(self, *args, **options):
        name = options['name']
        domain = options['domain']
        email = options.get('email')
        display_name = options.get('display_name')

        # Create slug from name
        slug = slugify(name)
        
        # Check if organization already exists
        if Organization.objects.filter(slug=slug).exists():
            raise CommandError(f'Organization with slug "{slug}" already exists')
        
        # Check if domain already exists
        if Domain.objects.filter(domain=domain).exists():
            raise CommandError(f'Domain "{domain}" is already registered')

        # Create organization
        org = Organization.objects.create(
            name=name,
            slug=slug,
            email_sender=email,
            email_display_name=display_name or name,
            is_active=True
        )

        # Create domain
        domain_obj = Domain.objects.create(
            organization=org,
            domain=domain,
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created tenant:\n'
                f'  Organization: {org.name} (slug: {org.slug})\n'
                f'  Domain: {domain_obj.domain}\n'
                f'  Email: {org.email_sender or "Not set"}\n'
                f'  Access URL: https://{domain}'
            )
        )

        # Provide next steps
        self.stdout.write(
            self.style.WARNING(
                f'\nNext steps:\n'
                f'1. Configure DNS to point {domain} to your server\n'
                f'2. Update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS in settings\n'
                f'3. Set up SSL certificate for {domain}\n'
                f'4. Create admin user for this organization'
            )
        )
