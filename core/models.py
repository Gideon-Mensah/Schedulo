from django.db import models
from core.tenant import get_current_org


class Organization(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Domain(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="domains")
    domain = models.CharField(max_length=255, unique=True)  # e.g. acme.localhost
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TenantManager(models.Manager):
    """Auto-scope queries by the current org (if present)."""
    def get_queryset(self):
        qs = super().get_queryset()
        org = get_current_org()
        return qs.filter(organization=org) if org else qs

class TenantOwned(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = TenantManager()             # default scoping
    all_objects = models.Manager()        # escape hatch (superuser/admin tasks)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.organization_id:
            org = get_current_org()
            if org is None:
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured("No current organization set when saving a tenant object.")
            self.organization = org
        return super().save(*args, **kwargs)
    