from django.urls import path

from . import views, miscs

urlpatterns = [
    path('', views.home),
    path('weibo/<str:uid>/', views.index, name='weibo'),
    path('miscs/dazuoshou/', miscs.dazuoshou),
    path('miscs/fangeqiang/', miscs.fangeqiang),
    path('miscs/letscorp/', miscs.letscorp),
    path('miscs/zaobaotoday/', miscs.zaobaotoday),
]
