from django.db import models
from .multitenancy import get_current_tenant

class TenantQuerySet(models.QuerySet):
    def for_current_tenant(self):
        tenant = get_current_tenant()
        if tenant is None:
            # Optional: raise to avoid data leaks
            return self.none()
        return self.filter(organization=tenant)

class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        return qs.filter(organization=tenant) if tenant else qs.none()
