from django.urls import path
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    path(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    path(r'^users/$', views.UserView.as_view()),
    # path(r'authorizations/', obtain_jwt_token),
    path(r'^authorizations/$', views.UserAuthorizationView.as_view()),  # 登录，获取JWT token
    path(r'^user/$', views.UserDetailView.as_view()),
    path(r'^browse_histories/$', views.UserBrowsingHistoryView.as_view()),

]

router = routers.DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')
urlpatterns += router.urls