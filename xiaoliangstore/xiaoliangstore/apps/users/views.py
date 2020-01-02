from rest_framework.response import Response
from rest_framework.views import APIView

from xiaoliangstore.apps.users.models import User


class UsernameCountView(APIView):
    """用户名统计"""
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)