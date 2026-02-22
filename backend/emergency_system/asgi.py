"""
ASGI config for emergency_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
<<<<<<< HEAD
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
=======
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
>>>>>>> origin/dev
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_system.settings')

application = get_asgi_application()
