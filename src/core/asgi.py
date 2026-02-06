"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import sys

# Ensure project root is on path (e.g. when run from Docker with CWD=/app)
_asgi_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _asgi_dir not in sys.path:
    sys.path.insert(0, _asgi_dir)
if "/src" not in sys.path and os.path.exists("/src"):
    sys.path.insert(0, "/src")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from django.core.asgi import get_asgi_application

application = get_asgi_application()
