from django.urls import path
from portfolio.views import save_instagram_media

urlpatterns = [
    path('', save_instagram_media, name='save_instagram_media'),
]
