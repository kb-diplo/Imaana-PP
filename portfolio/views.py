from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import (
    PortfolioItem, PortfolioImage,
    Package, QuoteRequest,
    ContactMessage, GalleryImage, ProfileImage, SiteSettings
)
from .forms import QuoteRequestForm, ContactForm


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = SiteSettings.objects.first()
        context.update({
            'featured_items': PortfolioItem.objects.filter(
                is_featured=True, published=True
            )[:6],
            'gallery_images': GalleryImage.objects.filter(is_active=True).order_by('order'),
            'profile_image': ProfileImage.objects.filter(is_active=True).first(),
            'digital_items': PortfolioItem.objects.filter(
                category='digital', published=True
            ).order_by('-created_at')[:3],
            'modelling_items': PortfolioItem.objects.filter(
                category='modelling', published=True
            ).order_by('-created_at')[:3],
            'site_settings': site_settings,
        })
        return context


class PortfolioListView(ListView):
    """View for listing all portfolio items with filtering."""
    model = PortfolioItem
    template_name = 'portfolio/portfolio_list.html'
    context_object_name = 'portfolio_items'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = PortfolioItem.objects.filter(published=True).order_by('-created_at')
        
        # Filter by category if provided
        category = self.request.GET.get('category')
        if category in ['digital', 'modelling']:
            queryset = queryset.filter(category=category)
            
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PortfolioDetailView(DetailView):
    """View for displaying a single portfolio item."""
    model = PortfolioItem
    template_name = 'portfolio/portfolio_detail.html'
    context_object_name = 'portfolio_item'
    
    def get_queryset(self):
        return PortfolioItem.objects.filter(published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_items'] = PortfolioItem.objects.filter(
            published=True,
            category=self.object.category
        ).exclude(pk=self.object.pk)[:3]
        
        # Add navigation context
        all_items = PortfolioItem.objects.filter(published=True).order_by('-created_at')
        current_index = list(all_items.values_list('id', flat=True)).index(self.object.id)
        
        if current_index > 0:
            context['previous_item'] = all_items[current_index - 1]
        if current_index < len(all_items) - 1:
            context['next_item'] = all_items[current_index + 1]
            
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'portfolio/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_image'] = ProfileImage.objects.filter(is_active=True).first()
        return context


class PackageListView(ListView):
    """View for listing all packages."""
    model = Package
    template_name = 'portfolio/packages.html'
    context_object_name = 'packages'
    
    def get_queryset(self):
        return Package.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['digital_packages'] = Package.objects.filter(
            category='digital',
            is_active=True
        )
        context['modelling_packages'] = Package.objects.filter(
            category='modelling',
            is_active=True
        )
        context['form'] = QuoteRequestForm()
        return context


class QuoteRequestView(FormView):
    """View for handling quote request submissions."""
    form_class = QuoteRequestForm
    template_name = 'portfolio/packages.html'
    success_url = reverse_lazy('packages')
    
    def form_valid(self, form):
        # Save the quote request
        package_id = self.request.POST.get('package')
        package = get_object_or_404(Package, id=package_id) if package_id else None
        
        quote = form.save(commit=False)
        if package:
            quote.package = package
        quote.save()
        
        # Send email notification
        try:
            subject = f'New Quote Request: {quote.name} - {package.name if package else "General Enquiry"}'
            message = f'''
            Name: {quote.name}
            Email: {quote.email}
            Phone: {quote.phone or 'Not provided'}
            Package: {package.name if package else 'General Enquiry'}
            
            Message:
            {quote.message}
            '''
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            import logging
            logger = logging.getLogger('portfolio')
            logger.error(f"Failed to send quote request email: {str(e)}")
            # Don't fail the form submission if email fails
        
        messages.success(
            self.request,
            'Thank you for your request! We will get back to you soon.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'There was an error with your submission. Please check the form and try again.'
        )
        return super().form_invalid(form)


class ContactView(FormView):
    """Contact page view."""
    template_name = 'portfolio/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        # Get the user's IP address
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')

        # Save the contact message to the database
        message = form.save(commit=False)
        message.is_responded = False  # Set initial status
        message.save()

        messages.success(
            self.request,
            'Your message has been sent successfully! I will get back to you soon.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'There was an error with your submission. Please check the form and try again.'
        )
        return super().form_invalid(form)


def custom_404_view(request, exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)


def custom_500_view(request):
    """Custom 500 error page."""
    return render(request, '500.html', status=500)


@require_POST
def save_instagram_media(request):
    """Webhook endpoint for Instagram media updates."""
    import logging
    logger = logging.getLogger('portfolio')
    
    try:
        # Verify webhook token for security
        webhook_token = request.META.get('HTTP_X_HUB_SIGNATURE_256')
        expected_token = settings.INSTAGRAM_WEBHOOK_TOKEN if hasattr(settings, 'INSTAGRAM_WEBHOOK_TOKEN') else None
        
        if not expected_token:
            logger.warning("Instagram webhook called but no token configured")
            return JsonResponse({'status': 'error', 'message': 'Webhook not configured'}, status=400)
        
        # This is a placeholder for Instagram webhook integration
        # In production, you would verify the webhook signature and process the data
        logger.info("Instagram webhook received")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Instagram webhook error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
