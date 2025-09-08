# IMA ANA Portfolio

A Django-based portfolio website for IMA ANA - Digital Creator & Professional Model.

## Features

- **Portfolio Management**: Showcase digital and modeling work
- **Gallery System**: Dynamic image gallery with admin management
- **Contact System**: Contact forms with admin notifications
- **Package Services**: Service packages for different categories
- **Custom Admin Interface**: Beautiful custom admin dashboard
- **Responsive Design**: Mobile-first responsive design
- **Social Media Integration**: Instagram and TikTok links

## Tech Stack

- **Backend**: Django 5.0.6
- **Frontend**: Bootstrap 5, Custom CSS
- **Database**: SQLite (development), PostgreSQL (production)
- **Media**: Pillow for image processing
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Static Files**: WhiteNoise for production

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kb-diplo/Imaana-PP.git
cd Imaana-PP
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Deployment

This project is configured for deployment on PythonAnywhere and other platforms.

### Environment Variables

Key environment variables (see `.env.example`):
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Add your domain
- `EMAIL_*`: Email configuration for contact forms

## Admin Interfaces

- **Default Admin**: `/admin/` - Portfolio items, packages, messages
- **Custom Admin**: `/custom-admin/` - Gallery images, profile images, site settings

## License

This project is proprietary software created exclusively for IMA ANA (Elsy). All rights reserved. See [LICENSE](LICENSE) for full terms.

**Repository**: https://github.com/kb-diplo/Imaana-PP.git

This software may not be used, copied, modified, or distributed without explicit written permission from IMA ANA (Elsy).
