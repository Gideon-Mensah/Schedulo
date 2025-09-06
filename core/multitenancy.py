from core.tenant import set_current_org
# core/multitenancy.py
from contextvars import ContextVar
from django.utils.deprecation import MiddlewareMixin
from django.db.utils import ProgrammingError, OperationalError
from .models import Domain

_current_tenant = ContextVar("current_tenant", default=None)

def get_current_tenant():
    return _current_tenant.get()

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(":")[0].lower()
        domain = Domain.objects.select_related("organization").filter(domain=host, is_active=True).first()
        org = domain.organization if domain else None
        request.tenant = org
        set_current_org(org)
