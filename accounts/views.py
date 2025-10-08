from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q

from .forms import UserUpdateForm, ProfileForm, CustomPasswordResetForm, IDCardForm
from .models import Profile, User

def register(request):
    # Block registration on Delaala domain
    from django.conf import settings
    host = request.get_host().split(":")[0]
    if host == getattr(settings, 'DELAALA_DOMAIN', ''):
        messages.error(request, 'Registration is not available on this portal. Please contact your administrator.')
        return redirect('/accounts/login/?error=signup_disabled')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

# accounts/views.py


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile})

@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "Profile updated.")
            return redirect("account_profile")
        messages.error(request, "Please fix the errors below.")
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileForm(instance=profile)
    return render(request, "accounts/profile_edit.html", {"uform": uform, "pform": pform})

class AccountPasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("account_password_change_done")
    form_class = CustomPasswordResetForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Remove 'user' from kwargs since SetPasswordForm expects it differently
        if 'user' in kwargs:
            kwargs.pop('user')
        # SetPasswordForm expects the user as the first positional argument
        return kwargs
    
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

class AccountPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"


# ID Card Views
from django.http import HttpResponse
from django.template.loader import get_template
from .models import IDCard, OrgMembership
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse


@method_decorator(staff_member_required, name='dispatch')
class IDCardListView(ListView):
    """List all ID cards for the organization"""
    model = IDCard
    template_name = 'accounts/id_card_list.html'
    context_object_name = 'id_cards'
    paginate_by = 20

    def get_queryset(self):
        # Get current organization from middleware
        org = getattr(self.request, 'tenant', None)
        if not org:
            return IDCard.objects.none()
        
        queryset = IDCard.objects.filter(organization=org).select_related('user', 'organization')
        
        # Add search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(department__icontains=search_query)
            ).distinct()
        
        return queryset.order_by('user__first_name', 'user__last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = getattr(self.request, 'tenant', None)
        context['organization'] = org
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator(staff_member_required, name='dispatch')
class IDCardDetailView(DetailView):
    """View individual ID card"""
    model = IDCard
    template_name = 'accounts/id_card_detail.html'
    context_object_name = 'id_card'

    def get_queryset(self):
        org = getattr(self.request, 'tenant', None)
        if not org:
            return IDCard.objects.none()
        return IDCard.objects.filter(organization=org)


@method_decorator(staff_member_required, name='dispatch')
class IDCardCreateView(CreateView):
    """Create new ID card for employee"""
    model = IDCard
    form_class = IDCardForm
    template_name = 'accounts/id_card_form.html'

    def form_valid(self, form):
        org = getattr(self.request, 'tenant', None)
        if not org:
            messages.error(self.request, "No organization selected.")
            return redirect('account_profile')
        form.instance.organization = org
        messages.success(self.request, "ID Card created successfully.")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        org = getattr(self.request, 'tenant', None)
        if org:
            kwargs['organization'] = org
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse('accounts:id_card_detail', kwargs={'pk': self.object.pk})


@method_decorator(staff_member_required, name='dispatch')
class IDCardUpdateView(UpdateView):
    """Update existing ID card"""
    model = IDCard
    form_class = IDCardForm
    template_name = 'accounts/id_card_form.html'

    def get_queryset(self):
        org = getattr(self.request, 'tenant', None)
        if not org:
            return IDCard.objects.none()
        return IDCard.objects.filter(organization=org)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        org = getattr(self.request, 'tenant', None)
        if org:
            kwargs['organization'] = org
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "ID Card updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('accounts:id_card_detail', kwargs={'pk': self.object.pk})


@staff_member_required
def id_card_print_view(request, pk):
    """Generate printable ID card with QR code"""
    org = getattr(request, 'tenant', None)
    if not org:
        messages.error(request, "No organization selected.")
        return redirect('accounts:id_card_list')
    
    id_card = get_object_or_404(IDCard, pk=pk, organization=org)
    
    # Generate QR code for verification URL
    verify_path = reverse("accounts:id_card_verify", args=[id_card.employee_id])
    absolute_url = request.build_absolute_uri(verify_path)
    qr_data_uri = _qr_data_uri(absolute_url)
    
    return render(request, 'accounts/id_card_print.html', {
        'id_card': id_card,
        'organization': org,
        'qr_data_uri': qr_data_uri,
    })


@login_required
def my_id_card_view(request):
    """User can view their own ID card"""
    org = getattr(request, 'tenant', None)
    if not org:
        messages.error(request, "No organization selected.")
        return redirect('account_profile')
    
    try:
        id_card = IDCard.objects.get(user=request.user, organization=org)
        return render(request, 'accounts/my_id_card.html', {
            'id_card': id_card,
            'organization': org,
        })
    except IDCard.DoesNotExist:
        messages.info(request, "You don't have an ID card yet. Please contact your administrator.")
        return redirect('account_profile')


@login_required
def employee_search(request):
    """AJAX endpoint for searching employees with pagination"""
    from django.http import JsonResponse
    
    q = (request.GET.get("q") or "").strip()
    page = int(request.GET.get("page", 1))
    page_size = 20

    # Get current organization from tenant middleware
    org = getattr(request, 'tenant', None)
    if not org:
        return JsonResponse({"results": [], "pagination": {"more": False}})

    # Filter users by organization and active status
    qs = User.objects.filter(
        is_active=True,
        profile__organization=org
    ).select_related('profile')

    # Apply search filter if query provided
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size

    results = []
    for user in qs.order_by("first_name", "last_name")[start:end]:
        # Create a nice display name
        full_name = user.get_full_name()
        if full_name:
            display_text = f"{full_name} ({user.username})"
        else:
            display_text = user.username
            
        # Add department info if available
        if hasattr(user, 'profile') and user.profile.job_title:
            display_text += f" - {user.profile.job_title}"
            
        results.append({
            "id": str(user.pk),
            "text": display_text
        })

    return JsonResponse({
        "results": results,
        "pagination": {"more": end < total}
    })

def _qr_data_uri(payload: str, box_size=8, border=2) -> str:
    """Generate a high-resolution QR code as a data URI for embedding in templates"""
    try:
        import qrcode
        from qrcode.image.pil import PilImage
        import io
        import base64
        
        img = qrcode.make(payload, image_factory=PilImage, box_size=box_size, border=border)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except ImportError:
        # Fallback if qrcode library not available
        return None

@login_required
def id_card_verify(request, employee_id):
    """Simple ID card verification endpoint for QR codes"""
    try:
        id_card = IDCard.objects.select_related('user', 'organization').get(
            employee_id=employee_id,
            is_active=True
        )
        
        return render(request, 'accounts/id_card_verify.html', {
            'id_card': id_card,
            'organization': id_card.organization,
            'is_valid': True,
        })
    except IDCard.DoesNotExist:
        return render(request, 'accounts/id_card_verify.html', {
            'employee_id': employee_id,
            'is_valid': False,
        })
