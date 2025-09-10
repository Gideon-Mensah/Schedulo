# core/middleware.py
import logging
from core.models import Organization
from core.org_context import org_context

logger = logging.getLogger(__name__)
ACTIVE_ORG_SESSION_KEY = "active_org_id"

class CurrentOrgMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 0) If a previous middleware (e.g., TenantMiddleware) already set tenant, keep it.
        org = getattr(request, "tenant", None)

        # 1) If not set, try session
        if org is None and hasattr(request, "session"):
            org_id = request.session.get(ACTIVE_ORG_SESSION_KEY)
            if org_id:
                try:
                    org = Organization.objects.get(pk=org_id)
                    logger.debug("Tenant resolved from session: %s", org_id)
                except Organization.DoesNotExist:
                    logger.info("Stale active_org_id=%s; clearing.", org_id)
                    request.session.pop(ACTIVE_ORG_SESSION_KEY, None)

        # 2) If still not set, fallback to user's profile org
        user = getattr(request, "user", None)
        if org is None and user is not None and getattr(user, "is_authenticated", False):
            profile = getattr(user, "profile", None)
            prof_org = getattr(profile, "organization", None) if profile else None
            if prof_org:
                org = prof_org
                if hasattr(request, "session"):
                    request.session[ACTIVE_ORG_SESSION_KEY] = org.pk
                logger.debug("Tenant resolved from user.profile.organization: %s", org.pk)
            else:
                logger.debug("Authenticated user has no profile.organization.")

        # 3) Attach only if we found one; otherwise leave any existing value untouched
        if org is not None:
            request.tenant = org
            # Activate context only when org exists
            with org_context(org):
                return self.get_response(request)

        logger.debug("No tenant resolved for path=%s", request.path)
        return self.get_response(request)