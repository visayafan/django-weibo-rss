import os

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
                  path('', include('rss.urls')),
              ] + static(settings.STATIC_URL)
