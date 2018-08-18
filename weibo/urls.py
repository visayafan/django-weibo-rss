from django.urls import path
from weibo import views

urlpatterns = [
    path('<str:uid>/', views.index)
]
