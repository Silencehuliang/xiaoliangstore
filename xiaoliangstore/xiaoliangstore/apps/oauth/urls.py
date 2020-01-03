from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^qq/authorization/$', views.OAuthQQURLView.as_view()),
]
