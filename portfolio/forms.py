from django import forms
from django.core.validators import EmailValidator
from .models import QuoteRequest, ContactMessage, Service


class QuoteRequestForm(forms.ModelForm):
    """Form for quote requests."""
    class Meta:
        model = QuoteRequest
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone (optional)'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us more about your project...',
                'required': 'required'
            }),
        }
        error_messages = {
            'name': {
                'required': 'Please enter your name.',
            },
            'email': {
                'required': 'Please enter your email address.',
                'invalid': 'Please enter a valid email address.',
            },
            'message': {
                'required': 'Please enter your message.',
            },
        }

    def clean_phone(self):
        """
        Validate phone number (optional).
        If provided, it should be at least 10 digits.
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) < 10:
                raise forms.ValidationError('Phone number must be at least 10 digits.')
        return phone


class ContactForm(forms.ModelForm):
    """Form for contact page."""
    
    service_interest = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate service choices from database
        service_choices = [('', 'Select a service...')]
        active_services = Service.objects.filter(is_active=True).order_by('order', 'name')
        for service in active_services:
            service_choices.append((service.name.lower().replace(' ', '_'), service.name))
        self.fields['service_interest'].choices = service_choices
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'service_interest', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone (optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'required': 'required'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your message...',
                'required': 'required'
            }),
        }
        error_messages = {
            'name': {
                'required': 'Please enter your name.',
            },
            'email': {
                'required': 'Please enter your email address.',
                'invalid': 'Please enter a valid email address.',
            },
            'subject': {
                'required': 'Please enter a subject.',
            },
            'message': {
                'required': 'Please enter your message.',
            },
        }

    def clean_phone(self):
        """
        Validate phone number (optional).
        If provided, it should be at least 10 digits.
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) < 10:
                raise forms.ValidationError('Phone number must be at least 10 digits.')
        return phone

    def clean_subject(self):
        """Ensure subject is not too long."""
        subject = self.cleaned_data.get('subject', '')
        if len(subject) > 200:
            raise forms.ValidationError('Subject is too long. Maximum 200 characters allowed.')
        return subject

    def clean_message(self):
        """Ensure message is not too long."""
        message = self.cleaned_data.get('message', '')
        if len(message) > 2000:
            raise forms.ValidationError('Message is too long. Maximum 2000 characters allowed.')
        return message
