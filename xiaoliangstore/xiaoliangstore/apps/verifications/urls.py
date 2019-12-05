from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path(r'image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
]
