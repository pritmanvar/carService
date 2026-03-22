"""
ASGI config for carService project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carService.settings')
import django
django.setup()
from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

apps.populate(settings.INSTALLED_APPS)

def get_application() -> FastAPI:
    app = FastAPI(title="Car Service", debug=settings.DEBUG)
    SECRET_KEY = "wqwq"
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    static_path = os.path.join(settings.BASE_DIR, "static")  # adjust if needed
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    app.mount("/", WSGIMiddleware(get_wsgi_application()))

    return app

app = get_application()