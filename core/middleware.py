# core/middleware.py
import logging
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout
from core.models import Organization
from core.org_context import org_context
from .org_utils import user_org_name

logger = logging.getLogger(__name__)
ACTIVE_ORG_SESSION_KEY = "active_org_id"

class DelaalaDomainOrgLockMiddleware:
    """
    Middleware to restrict portal.delaala.co.uk access to only Delaala Company Limited users.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]

        if host == getattr(settings, 'DELAALA_DOMAIN', ''):
            if request.user.is_authenticated and not request.user.is_superuser:
                org = (user_org_name(request.user) or "").strip().lower()
                delaala_org = getattr(settings, 'DELAALA_ORG_NAME', '').lower()
                
                if org != delaala_org:
                    logger.warning(f"User {request.user.username} with org '{org}' attempted to access Delaala domain")
                    logout(request)
                    # Redirect to login with error message
                    return redirect("/accounts/login/?error=not_authorized")

        return self.get_response(request)

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