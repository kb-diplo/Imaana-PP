#!/usr/bin/env python
"""
Debug script to test contact form submission and identify issues.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elsy_portfolio.settings')
django.setup()

from portfolio.forms import ContactForm
from portfolio.models import ContactMessage, Service

def test_contact_form():
    """Test contact form validation and saving."""
    print("=== Contact Form Debug Test ===")
    
    # Check if services exist
    services = Service.objects.filter(is_active=True)
    print(f"Active services found: {services.count()}")
    for service in services:
        print(f"  - {service.name} (order: {service.order})")
    
    # Test form with valid data
    test_data = {
        'name': 'Debug Test User',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'service_interest': 'digital_content_creation',
        'subject': 'Test Subject Debug',
        'message': 'This is a test message to debug the contact form.'
    }
    
    print(f"\nTesting form with data: {test_data}")
    
    # Create form instance
    form = ContactForm(data=test_data)
    
    print(f"Form is valid: {form.is_valid()}")
    
    if not form.is_valid():
        print("Form validation errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
    else:
        print("Form is valid, attempting to save...")
        try:
            # Save the form
            message = form.save(commit=False)
            message.is_responded = False
            message.save()
            print(f"SUCCESS: Message saved successfully! ID: {message.id}")
            
            # Verify it's in the database
            saved_message = ContactMessage.objects.get(id=message.id)
            print(f"SUCCESS: Message verified in database: {saved_message.name} - {saved_message.subject}")
            
        except Exception as e:
            print(f"ERROR: Error saving message: {e}")
            import traceback
            traceback.print_exc()
    
    # Check total messages in database
    total_messages = ContactMessage.objects.count()
    print(f"\nTotal messages in database: {total_messages}")
    
    # List all messages
    print("\nAll messages in database:")
    for i, msg in enumerate(ContactMessage.objects.all().order_by('-created_at'), 1):
        print(f"  {i}. {msg.name} - {msg.subject} ({msg.created_at})")

def test_form_choices():
    """Test form service choices generation."""
    print("\n=== Form Choices Test ===")
    form = ContactForm()
    choices = form.fields['service_interest'].choices
    print(f"Service choices available: {len(choices)}")
    for value, label in choices:
        print(f"  '{value}' -> '{label}'")

if __name__ == '__main__':
    test_contact_form()
    test_form_choices()
