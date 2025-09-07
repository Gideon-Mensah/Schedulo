from core.models import Organization
from core.org_context import org_context

ACTIVE_ORG_SESSION_KEY = "active_org_id"

class CurrentOrgMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        org = None

        # 1) session-selected org
        org_id = request.session.get(ACTIVE_ORG_SESSION_KEY) if hasattr(request, "session") else None
        if org_id:
            try:
                org = Organization.objects.get(pk=org_id)
            except Organization.DoesNotExist:
                org = None

        # 2) fallback to user's profile org (ONLY if request.user exists & is authenticated)
        user = getattr(request, "user", None)
        if org is None and user is not None and getattr(user, "is_authenticated", False):
            try:
                org = user.profile.organization
                request.session[ACTIVE_ORG_SESSION_KEY] = org.pk
            except Exception:
                pass

        # attach tenant
        request.tenant = org

        # activate tenant context for the request
        if org is not None:
            with org_context(org):
                return self.get_response(request)

        return self.get_response(request)
