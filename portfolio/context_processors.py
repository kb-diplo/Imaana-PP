from .models import SiteSettings

def site_settings(request):
    """Context processor to make site settings available in all templates."""
    settings = SiteSettings.objects.first()
    return {
        'site_settings': settings
    }
