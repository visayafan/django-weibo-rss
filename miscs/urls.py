from django.urls import path

from miscs import views

# miscs此app与生成微博订阅源没有关系，纯粹是私用备份方便
urlpatterns=[
    path('dazuoshou/', views.dazuoshou),
    path('fangeqiang/', views.fangeqiang)
]