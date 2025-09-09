from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import (
    GalleryImage, ProfileImage, ContactMessage, SiteSettings
)
from .admin import GalleryImageAdmin, ProfileImageAdmin


class PortfolioAdminSite(AdminSite):
    site_header = 'Imaana Portfolio Management'
    site_title = 'Portfolio Admin'
    index_title = 'Content Management Dashboard'
    site_url = '/'
    index_template = 'custom_admin/admin/index.html'
    
    def has_permission(self, request):
        """
        Check if the given HttpRequest has permission to view the admin index page.
        """
        return request.user.is_active and request.user.is_staff
    
    def index(self, request, extra_context=None):
        """
        Display the main admin index page with dashboard statistics.
        """
        extra_context = extra_context or {}
        
        # Get statistics for dashboard
        extra_context.update({
            'gallery_count': GalleryImage.objects.count(),
            'profile_count': ProfileImage.objects.count(),
            'message_count': ContactMessage.objects.filter(is_responded=False).count(),
            'active_gallery_count': GalleryImage.objects.filter(is_active=True).count(),
            'active_profile_count': ProfileImage.objects.filter(is_active=True).count(),
            'recent_messages': ContactMessage.objects.order_by('-created_at')[:5],
            'latest_gallery': GalleryImage.objects.order_by('-created_at').first(),
            'latest_profile': ProfileImage.objects.order_by('-created_at').first(),
            'latest_message': ContactMessage.objects.order_by('-created_at').first(),
        })
        
        return super().index(request, extra_context)


# Create custom admin site instance
portfolio_admin_site = PortfolioAdminSite(name='portfolio_admin')


class CustomGalleryImageAdmin(GalleryImageAdmin):
    """Custom Gallery Image Admin for simplified client interface"""
    change_list_template = 'custom_admin/change_list.html'
    change_form_template = 'custom_admin/change_form.html'
    list_display = ('title', 'thumbnail_preview', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    actions = ['activate_images', 'deactivate_images']
    
    def activate_images(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} images were successfully activated.')
    activate_images.short_description = "Activate selected images"
    
    def deactivate_images(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} images were successfully deactivated.')
    deactivate_images.short_description = "Deactivate selected images"
    
    def thumbnail_preview(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; border: 2px solid #e9ecef;" />',
                    obj.image.url
                )
            except:
                return format_html('<span class="badge bg-danger">Image Error</span>')
        return format_html('<span class="badge bg-secondary">No Image</span>')
    thumbnail_preview.short_description = "Preview"


class CustomProfileImageAdmin(ProfileImageAdmin):
    """Custom Profile Image Admin for simplified client interface"""
    change_list_template = 'custom_admin/change_list.html'
    change_form_template = 'custom_admin/change_form.html'
    list_display = ('title', 'thumbnail_preview', 'is_active', 'created_at')
    list_editable = ('is_active',)
    actions = ['activate_images', 'deactivate_images']
    
    def activate_images(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} profile images were successfully activated.')
    activate_images.short_description = "Activate selected profile images"
    
    def deactivate_images(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} profile images were successfully deactivated.')
    deactivate_images.short_description = "Deactivate selected profile images"
    
    def thumbnail_preview(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; border: 2px solid #e9ecef;" />',
                    obj.image.url
                )
            except:
                return format_html('<span class="badge bg-danger">Image Error</span>')
        return format_html('<span class="badge bg-secondary">No Image</span>')
    thumbnail_preview.short_description = "Preview"


class CustomSiteSettingsAdmin(admin.ModelAdmin):
    """Custom Site Settings Admin for client-friendly configuration"""
    change_form_template = 'custom_admin/change_form.html'
    list_display = ('site_name', 'hero_title', 'hero_subtitle', 'main_profile_image', 'updated_at')
    fieldsets = (
        ('🏠 Site Information', {
            'fields': ('site_name', 'site_description'),
            'description': 'Basic site information and branding'
        }),
        ('👤 Profile Settings', {
            'fields': ('main_profile_image',),
            'description': 'Select the main profile image to display across the site'
        }),
        ('✨ Hero Section', {
            'fields': ('hero_title', 'hero_subtitle'),
            'description': 'Main taglines displayed on your homepage'
        }),
        ('📱 Social Media Links', {
            'fields': ('instagram_url', 'tiktok_url'),
            'description': 'Your social media profile URLs'
        }),
        ('📞 Contact Information', {
            'fields': ('email', 'phone', 'whatsapp_number', 'address'),
            'description': 'Contact details for clients to reach you'
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        if not SiteSettings.objects.exists():
            from django.shortcuts import redirect
            return redirect('portfolio_admin:portfolio_sitesettings_add')
        return super().changelist_view(request, extra_context)


class CustomContactMessageAdmin(admin.ModelAdmin):
    """Custom Contact Message Admin for client message management"""
    change_list_template = 'custom_admin/change_list.html'
    change_form_template = 'custom_admin/contact_message_detail.html'
    list_display = ('name', 'email', 'service_interest', 'subject', 'is_responded', 'created_at')
    list_filter = ('is_responded', 'service_interest', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message', 'service_interest')
    list_editable = ('is_responded',)
    readonly_fields = ('name', 'email', 'phone', 'service_interest', 'subject', 'message', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'phone', 'service_interest', 'subject', 'message', 'created_at')
        }),
        ('Response Status', {
            'fields': ('is_responded',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Custom logic for marking messages as responded when viewed
        if request.method == 'POST' and 'mark_responded' in request.POST:
            obj = get_object_or_404(ContactMessage, pk=object_id)
            if not obj.is_responded:
                obj.is_responded = True
                obj.save()
                self.message_user(request, f"Message from {obj.name} marked as responded.")
        elif request.method == 'POST' and 'mark_unresponded' in request.POST:
            obj = get_object_or_404(ContactMessage, pk=object_id)
            if obj.is_responded:
                obj.is_responded = False
                obj.save()
                self.message_user(request, f"Message from {obj.name} marked as unresponded.")
        
        return super().change_view(request, object_id, form_url, extra_context)


# Register models with custom admin site
portfolio_admin_site.register(GalleryImage, CustomGalleryImageAdmin)
portfolio_admin_site.register(ProfileImage, CustomProfileImageAdmin)
portfolio_admin_site.register(ContactMessage, CustomContactMessageAdmin)
portfolio_admin_site.register(SiteSettings, CustomSiteSettingsAdmin)
