from contextlib import contextmanager
from core.tenant import set_current_org, get_current_org

@contextmanager
def org_context(org):
    prev = get_current_org()
    set_current_org(org)
    try:
        yield
    finally:
        set_current_org(prev)
