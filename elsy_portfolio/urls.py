"""
URL configuration for elsy_portfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import TemplateView
from portfolio.views import (
    HomeView, AboutView, ContactView, 
    PackageListView, QuoteRequestView,
    custom_404_view, custom_500_view
)
from portfolio.custom_admin import portfolio_admin_site

# Admin site configuration
admin.site.site_header = 'Elsy Portfolio Admin'
admin.site.site_title = 'Elsy Portfolio Administration'
admin.site.index_title = 'Site Administration'

def redirect_to_home(request):
    return redirect('home')

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),
    path('custom-admin/', portfolio_admin_site.urls),
    
    # Main site URLs
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('packages/', PackageListView.as_view(), name='packages'),
    path('quote/', QuoteRequestView.as_view(), name='quote_request'),
    
    # Portfolio URLs (disabled - using gallery instead)
    # path('portfolio/', include('portfolio.urls')),
    
    # API URLs
    path('api/', include('portfolio.api.urls')),
    
    # Authentication URLs (for future use)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Robots.txt and sitemap.xml (for SEO)
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', 
        content_type='text/plain'
    )),
    
    # Favicon (redirect to static file)
    path('favicon.ico', redirect('/static/img/favicon.ico')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
