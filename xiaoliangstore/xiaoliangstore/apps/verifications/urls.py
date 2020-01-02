from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
]
