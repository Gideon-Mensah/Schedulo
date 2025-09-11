# core/tenant.py
from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Type-only import to avoid circular import at runtime
    from .models import Organization

# Store the actual Organization instance (no runtime import needed)
_CURRENT_ORG: ContextVar[Optional["Organization"]] = ContextVar("CURRENT_ORG", default=None)

def set_current_org(org: Optional["Organization"]) -> None:
    _CURRENT_ORG.set(org)

def get_current_org() -> Optional["Organization"]:
    return _CURRENT_ORG.get()

class org_context:
    """with org_context(org): activate current org for this block."""
    def __init__(self, org: Optional["Organization"]):
        self.org = org
        self._token = None

    def __enter__(self):
        self._token = _CURRENT_ORG.set(self.org)
        return self.org

    def __exit__(self, exc_type, exc, tb):
        if self._token is not None:
            _CURRENT_ORG.reset(self._token)
