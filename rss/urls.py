from django.urls import path
from . import views, miscs

urlpatterns = [
    path('<str:uid>/', views.index),
    path('dazuoshou/', miscs.dazuoshou),
    path('fangeqiang/', miscs.fangeqiang)
]
