import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elsy_portfolio.settings')
django.setup()

from portfolio.models import ContactMessage, GalleryImage

# Check all messages in database
print('All messages in database:')
for msg in ContactMessage.objects.all().order_by('-created_at'):
    print(f'ID: {msg.id}, Name: {msg.name}, Subject: {msg.subject}, Service: {msg.service_interest}, Created: {msg.created_at}')

print(f'\nTotal messages: {ContactMessage.objects.count()}')

# Check gallery images
print('\nGallery Images:')
for img in GalleryImage.objects.all():
    print(f'ID: {img.id}, Title: {img.title}, Active: {img.is_active}')

print(f'\nTotal gallery images: {GalleryImage.objects.count()}')
