from django.urls import path
from . import views

urlpatterns = [
    path(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    path(r'^users/$', views.UserView.as_view()),
]
