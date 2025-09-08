from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import reverse, path
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import (
    PortfolioItem, PortfolioImage, Package, 
    QuoteRequest, ContactMessage, GalleryImage, ProfileImage, SiteSettings
)


class PortfolioAdminSite(AdminSite):
    site_header = 'Portfolio Admin'
    site_title = 'Portfolio Admin'
    index_title = 'Portfolio Management'
    site_url = '/'
    
    def index(self, request, extra_context=None):
        """Custom dashboard with stats"""
        extra_context = extra_context or {}
        extra_context.update({
            'gallery_count': GalleryImage.objects.count(),
            'messages_count': ContactMessage.objects.filter(is_responded=False).count(),
            'portfolio_count': PortfolioItem.objects.count(),
            'packages_count': Package.objects.count(),
            'profile_count': ProfileImage.objects.count(),
        })
        return render(request, 'custom_admin/index.html', extra_context)
    


# Create custom admin site instance
portfolio_admin_site = PortfolioAdminSite(name='portfolio_admin')


# Admin classes
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'thumbnail_preview', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active', 'order')
    search_fields = ('title', 'alt_text', 'caption')
    ordering = ('order', '-created_at')
    actions = ['activate_images', 'deactivate_images']
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    thumbnail_preview.short_description = "Preview"
    
    def activate_images(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} images activated.")
    activate_images.short_description = "Activate selected images"
    
    def deactivate_images(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} images deactivated.")
    deactivate_images.short_description = "Deactivate selected images"


class ProfileImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'thumbnail_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    actions = ['activate_images', 'deactivate_images']
    
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    thumbnail_preview.short_description = "Preview"
    
    def activate_images(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} images activated.")
    activate_images.short_description = "Activate selected images"
    
    def deactivate_images(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} images deactivated.")
    deactivate_images.short_description = "Deactivate selected images"


# Custom admin classes with custom templates
class CustomSiteSettingsAdmin(admin.ModelAdmin):
    change_form_template = 'custom_admin/change_form.html'
    fieldsets = (
        ('Main Text', {
            'fields': ('hero_title', 'hero_subtitle')
        }),
        ('Social Media', {
            'fields': ('instagram_url', 'tiktok_url', 'whatsapp_number')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


class CustomContactMessageAdmin(admin.ModelAdmin):
    change_list_template = 'custom_admin/change_list.html'
    change_form_template = 'custom_admin/contact_message_detail.html'
    list_display = ('name', 'email', 'subject', 'is_responded', 'created_at')
    list_filter = ('is_responded', 'created_at')
    list_editable = ('is_responded',)
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'created_at')
    ordering = ('-created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    
    def has_add_permission(self, request):
        return False
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Custom change view to handle message actions"""
        obj = self.get_object(request, object_id)
        
        if request.method == 'POST':
            if 'mark_responded' in request.POST:
                obj.is_responded = True
                obj.save()
                self.message_user(request, f"Message from {obj.name} marked as responded.")
            elif 'mark_unresponded' in request.POST:
                obj.is_responded = False
                obj.save()
                self.message_user(request, f"Message from {obj.name} marked as unresponded.")
        
        return super().change_view(request, object_id, form_url, extra_context)


# Update admin classes to use custom templates
class CustomGalleryImageAdmin(GalleryImageAdmin):
    change_list_template = 'custom_admin/change_list.html'
    change_form_template = 'custom_admin/change_form.html'

class CustomProfileImageAdmin(ProfileImageAdmin):
    change_list_template = 'custom_admin/change_list.html'
    change_form_template = 'custom_admin/change_form.html'

# Register models with custom admin site
portfolio_admin_site.register(GalleryImage, CustomGalleryImageAdmin)
portfolio_admin_site.register(ProfileImage, CustomProfileImageAdmin)
portfolio_admin_site.register(SiteSettings, CustomSiteSettingsAdmin)
portfolio_admin_site.register(ContactMessage, CustomContactMessageAdmin)
