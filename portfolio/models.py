from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created' and 'modified' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class PortfolioItem(TimeStampedModel):
    """Model representing a portfolio item (digital or modelling work)."""
    DIGITAL = 'digital'
    MODELLING = 'modelling'
    
    CATEGORY_CHOICES = [
        (DIGITAL, 'Digital Creator'),
        (MODELLING, 'Modelling'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=DIGITAL,
    )
    main_image = models.ImageField(
        upload_to='portfolio/main_images/%Y/%m/%d/',
        blank=True,
        help_text='Main image for the portfolio item.'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Mark as featured to display on the homepage.'
    )
    published = models.BooleanField(
        default=True,
        help_text='Set to False to hide this item from the public site.'
    )
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('portfolio:detail', kwargs={'slug': self.slug})


class PortfolioImage(TimeStampedModel):
    """Additional images for a portfolio item."""
    portfolio_item = models.ForeignKey(
        PortfolioItem,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='portfolio/images/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.portfolio_item.title} - {self.caption or 'Image'}"


class Package(TimeStampedModel):
    """Model for different service packages."""
    DIGITAL = 'digital'
    MODELLING = 'modelling'
    
    CATEGORY_CHOICES = [
        (DIGITAL, 'Digital Creator'),
        (MODELLING, 'Modelling'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=DIGITAL,
    )
    image = models.ImageField(
        upload_to='packages/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='Optional image for the package.'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Set to False to hide this package from the public site.'
    )
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.get_category_display()}-{self.name}")
        super().save(*args, **kwargs)


class QuoteRequest(TimeStampedModel):
    """Model for storing quote requests from the packages page."""
    package = models.ForeignKey(
        Package,
        related_name='quote_requests',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    is_contacted = models.BooleanField(
        default=False,
        help_text='Mark as contacted once you have responded to this request.'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quote Request'
        verbose_name_plural = 'Quote Requests'
    
    def __str__(self):
        return f"Quote request from {self.name} ({self.email})"


class ContactMessage(TimeStampedModel):
    """Model for storing contact form submissions."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_responded = models.BooleanField(
        default=False,
        help_text='Mark as responded once you have replied to this message.'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


class GalleryImage(TimeStampedModel):
    """Model for gallery images displayed on homepage."""
    title = models.CharField(max_length=200, blank=True, help_text='Auto-generated from filename')
    image = models.ImageField(upload_to='gallery/%Y/%m/%d/')
    alt_text = models.CharField(max_length=200, blank=True, help_text='Alternative text for accessibility')
    caption = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Order of display (lower numbers first)')
    is_active = models.BooleanField(
        default=True,
        help_text='Set to False to hide this image from the gallery.'
    )
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'
    
    def save(self, *args, **kwargs):
        # Auto-generate title from filename if not provided
        if not self.title and self.image:
            import os
            filename = os.path.basename(self.image.name)
            # Remove extension and clean up filename
            title = os.path.splitext(filename)[0]
            # Replace underscores and hyphens with spaces, capitalize
            title = title.replace('_', ' ').replace('-', ' ').title()
            self.title = title
        
        # Auto-generate alt_text from title if not provided
        if not self.alt_text and self.title:
            self.alt_text = self.title
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title or f"Gallery Image {self.id}"


class ProfileImage(models.Model):
    """Model for profile images used across the site."""
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='profile/')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', '-created_at']
        verbose_name = "Profile Image"
        verbose_name_plural = "Profile Images"
    
    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """Model for managing site-wide settings and social media links."""
    site_name = models.CharField(max_length=100, default="IMA ANA Portfolio")
    site_description = models.TextField(default="Digital Creator & Professional Model")
    instagram_url = models.URLField(blank=True, help_text="Instagram profile URL")
    tiktok_url = models.URLField(blank=True, help_text="TikTok profile URL", default="https://www.tiktok.com/@lcmukiri?_t=ZM-8zYQ4OgHYE2&_r=1")
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="WhatsApp number with country code")
    email = models.EmailField(blank=True, help_text="Contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    address = models.TextField(blank=True, help_text="Business address")
    hero_title = models.CharField(max_length=100, default="IMA ANA")
    hero_subtitle = models.CharField(max_length=200, default="Digital Creator & Professional Model")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return f"Site Settings - {self.site_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("Only one SiteSettings instance is allowed")
        super().save(*args, **kwargs)


