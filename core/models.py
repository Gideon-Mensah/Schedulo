from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Organization(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)  # e.g. "acme"
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="owned_orgs")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Domain(models.Model):
    """
    Maps incoming hostnames to an Organization.
    e.g. acme.schedulo.com -> acme org
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="domains")
    domain = models.CharField(max_length=255, unique=True)  # host only, no scheme
    is_primary = models.BooleanField(default=False)

class TenantOwned(models.Model):
    """
    Inherit this in every model that belongs to one org.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, editable=False, db_index=True)

    class Meta:
        abstract = True
