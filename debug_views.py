# Debug view to test ID card form context
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from core.models import Organization

User = get_user_model()

@staff_member_required
def debug_id_card_form(request):
    """Debug view to check what users would appear in ID card form"""
    
    # Get organization from request (same as the actual form)
    org = getattr(request, 'tenant', None)
    
    context = {
        'tenant_org': org,
        'tenant_org_name': org.name if org else 'None',
        'request_user': request.user,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
    }
    
    if org:
        # Same query as the actual form (matching shift booking system)
        queryset = User.objects.filter(
            profile__organization=org
        ).order_by('first_name', 'last_name')
        context['available_users'] = list(queryset)
        context['user_count'] = queryset.count()
    else:
        context['available_users'] = []
        context['user_count'] = 0
        context['error'] = 'No organization found in request.tenant'
    
    # Also get all organizations for debugging
    context['all_orgs'] = list(Organization.objects.all())
    
    return render(request, 'debug_id_card.html', context)
