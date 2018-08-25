from django.urls import path

from . import views, miscs

urlpatterns = [
    path('weibo/<str:uid>/', views.index),
    path('miscs/dazuoshou/', miscs.dazuoshou),
    path('miscs/fangeqiang/', miscs.fangeqiang),
]
