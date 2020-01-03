from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    re_path(r'^users/$', views.UserView.as_view()),
]
