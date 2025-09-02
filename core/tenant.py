# core/tenant.py
import contextvars
_current_org = contextvars.ContextVar("current_org", default=None)

def set_current_org(org): _current_org.set(org)
def get_current_org():    return _current_org.get()
