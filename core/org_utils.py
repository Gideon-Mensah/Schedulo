# core/org_utils.py
def user_org_name(user):
    """
    Helper function to get a user's organization name.
    Checks multiple possible relations based on your model structure.
    """
    # Option A: direct field
    if hasattr(user, "organization") and getattr(user.organization, "name", None):
        return user.organization.name

    # Option B: profile relation (most likely for your setup)
    if hasattr(user, "profile") and getattr(user.profile, "organization", None):
        return user.profile.organization.name

    # Option C: membership (first org)
    if hasattr(user, "memberships"):
        m = user.memberships.select_related("organization").first()
        if m and m.organization:
            return m.organization.name

    return None
