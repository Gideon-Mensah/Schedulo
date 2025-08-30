# compliance/utils.py
from __future__ import annotations
from typing import Iterable
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ComplianceDocument, ComplianceDocType
from .models import AuditLog, AuditAction
from datetime import date

from .models import ComplianceDocType, ComplianceDocument

# ---- 1) Define which doc types are required for each role ----
# Use the *names* of your ComplianceDocType rows exactly as they appear in the DB.
# Adjust as needed for your project.
ROLE_DOC_RULES = {
    "Care": [
        "DBS Check",
        "Right to Work",
        "Mandatory Training",  # e.g., Care Certificate / Basic Life Support, etc.
    ],
    "Cleaning": [
        "Right to Work",
        # add others if required
    ],
    # default for any other/unknown roles:
    "_DEFAULT": ["Right to Work"],
}

def required_types_for_role(role: str):
    """
    Returns a queryset of ComplianceDocType required for the given role.
    No DB schema change needed; we match by name.
    """
    names = ROLE_DOC_RULES.get(role) or ROLE_DOC_RULES["_DEFAULT"]
    return ComplianceDocType.objects.filter(is_active=True, name__in=names)


# ---- 2) Compliance check for a user vs a role ----
def _has_valid_document(user, doc_type: ComplianceDocType) -> bool:
    """
    A document is valid if:
      - status = approved
      - if the doc type requires expiry -> the document has a future (or today) expiry_date
    """
    qs = ComplianceDocument.objects.filter(
        user=user,
        doc_type=doc_type,
        status="approved",
    )

    if doc_type.requires_expiry:
        today = date.today()
        qs = qs.filter(expiry_date__isnull=False, expiry_date__gte=today)

    return qs.exists()


def user_is_compliant_for_role(user, role: str) -> bool:
    """
    True only if the user holds a valid doc for every required type for that role.
    """
    req_types = list(required_types_for_role(role))
    if not req_types:
        # If you prefer "no required docs means compliant", keep True.
        # If you prefer the opposite, return False here.
        return True

    for dt in req_types:
        if not _has_valid_document(user, dt):
            return False
    return True


def log_audit(*, actor=None, subject=None, action:str, shift=None, booking=None, message:str="", **extra):
    AuditLog.objects.create(
        actor=actor,
        subject=subject,
        action=action,
        shift=shift,
        booking=booking,
        message=message or "",
        extra=extra or {},
    )
