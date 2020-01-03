from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CreateUserSerializer
from .models import User


class UsernameCountView(APIView):
    """用户名统计"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


class UserView(CreateAPIView):
    """创建用户"""
    serializer_class = CreateUserSerializer
