from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from core.models import Organization

ACTIVE_ORG_SESSION_KEY = "active_org_id"

class CurrentOrgMiddleware(MiddlewareMixin):
    def process_request(self, request):
        org = None
        # (A) Subdomain/host routing (optional)
        # org = resolve_org_from_host(request.get_host())
        # (B) Session
        if org is None:
            org_id = request.session.get(ACTIVE_ORG_SESSION_KEY)
            if org_id:
                try:
                    org = Organization.objects.get(pk=org_id)
                except Organization.DoesNotExist:
                    org = None
        # (C) Fallback to user profile
        if org is None and request.user.is_authenticated:
            try:
                org = request.user.profile.organization
                request.session[ACTIVE_ORG_SESSION_KEY] = org.pk
            except Exception:
                pass
        request.tenant = org
        # Activate tenant context for ORM
        if org is not None:
            request._org_ctx = Organization.as_current(org)
            request._org_ctx.__enter__()
    def process_response(self, request, response):
        ctx = getattr(request, "_org_ctx", None)
        if ctx:
            ctx.__exit__(None, None, None)
        return response
