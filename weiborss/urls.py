from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('weibo/', include('weibo.urls')),
    path('miscs/', include('miscs.urls'))
]
