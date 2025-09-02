import os
from django.utils.text import slugify
from core.multitenancy import get_current_tenant

def tenant_upload_to(subfolder):
    def _path(instance, filename):
        tenant = get_current_tenant()
        tslug = tenant.slug if tenant else "global"
        return os.path.join("tenants", tslug, subfolder, filename)
    return _path
