from rest_framework import serializers
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializer import CreateUserSerializer


class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


class UserView(CreateAPIView):
    serializer_class = CreateUserSerializer


class UserDetailView(RetrieveAPIView):
    """用户详情信息
    """
    serializer_class = serializers.UserDetailSerializer
    # 补充通过认证才能访问接口的权限
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        返回请求的用户对象
        :return: user
        """
        return self.request.user
