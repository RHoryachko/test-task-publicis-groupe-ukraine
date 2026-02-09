"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

# Ensure project root is on path (e.g. when run from Docker with CWD=/app)
_wsgi_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _wsgi_dir not in sys.path:
    sys.path.insert(0, _wsgi_dir)
if "/src" not in sys.path and os.path.exists("/src"):
    sys.path.insert(0, "/src")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
