"""
WSGI config for rule2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rule2.settings")
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rule2.settings_zc_dev")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
