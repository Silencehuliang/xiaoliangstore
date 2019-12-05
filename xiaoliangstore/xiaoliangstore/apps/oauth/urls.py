from django.urls import path
from . import views

urlpatterns = [
    path(r'^qq/user/$', views.OAuthQQURLView.as_view()),
]
