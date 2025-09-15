from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve as dj_serve
from core.views import index, health
import os, re

urlpatterns = [
    path("", index, name="index"),
    path("health/", health, name="health"),
    path("", include("accounts.urls")),
    path("offers/", include("offers.urls")),
    path("api/", include("offers.api_urls")),
    path("api/", include("tickets.api_urls")),
    path("", include("tickets.urls")),
    path("", include("orders.urls")),
    path("admin/", admin.site.urls),
]

# Servir /media/ même quand DEBUG=0 (utile sur Fly avec le volume monté)
if os.getenv("SERVE_MEDIA", "1") == "1":
    prefix = re.escape(settings.MEDIA_URL.lstrip("/"))
    urlpatterns += [
        re_path(rf"^{prefix}(?P<path>.*)$", dj_serve, {"document_root": settings.MEDIA_ROOT}),
    ]
