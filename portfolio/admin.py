from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PortfolioItem, PortfolioImage, Package, 
    QuoteRequest, ContactMessage, GalleryImage, ProfileImage, SiteSettings, Service
)


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1
    fields = ('image', 'caption', 'order')
    classes = ('collapse',)


class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'thumbnail_preview', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active', 'order')
    search_fields = ('title', 'alt_text', 'caption')
    ordering = ('order', '-created_at')
    actions = ['activate_images', 'deactivate_images']
    fields = ('title', 'image', 'alt_text', 'caption', 'order', 'is_active')
    
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
    ordering = ('-is_active', '-created_at')
    
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    thumbnail_preview.short_description = "Preview"


class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'published', 'created_at')
    list_filter = ('category', 'is_featured', 'published', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PortfolioImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'category', 'main_image')
        }),
        ('Visibility', {
            'fields': ('is_featured', 'published'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'
    list_per_page = 20


class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'portfolio_item', 'caption', 'order')
    list_display_links = ('thumbnail_preview', 'portfolio_item')
    list_editable = ('order',)
    list_filter = ('portfolio_item__category',)
    search_fields = ('portfolio_item__title', 'caption')
    list_per_page = 20
    
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "No Image"
    thumbnail_preview.short_description = 'Preview'


class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'image')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20


class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'package', 'is_contacted', 'created_at')
    list_filter = ('is_contacted', 'created_at', 'package__category')
    search_fields = ('name', 'email', 'package__name', 'message')
    list_editable = ('is_contacted',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Requester Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Request Details', {
            'fields': ('package', 'message')
        }),
        ('Status', {
            'fields': ('is_contacted',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20
    
    def has_add_permission(self, request):
        # Disable adding new quote requests from admin
        return False


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_responded', 'created_at')
    list_filter = ('is_responded', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_responded',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Sender Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_responded',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20
    
    def has_add_permission(self, request):
        # Disable adding new contact messages from admin
        return False


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active', 'order')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active', 'order')
        }),
    )


class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'hero_title', 'hero_subtitle', 'updated_at')
    fieldsets = (
        ('🏠 Site Information', {
            'fields': ('site_name', 'site_description'),
            'description': 'Basic site information and branding'
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
        # Only allow adding if no instance exists
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Never allow deletion
        return False
    
    def changelist_view(self, request, extra_context=None):
        # If no settings exist, redirect to add form
        if not SiteSettings.objects.exists():
            from django.shortcuts import redirect
            return redirect('admin:portfolio_sitesettings_add')
        return super().changelist_view(request, extra_context)


# Register models with default admin site
admin.site.register(PortfolioItem, PortfolioItemAdmin)
admin.site.register(PortfolioImage, PortfolioImageAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(QuoteRequest, QuoteRequestAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)

# Note: GalleryImage and ProfileImage are registered with custom admin site only
