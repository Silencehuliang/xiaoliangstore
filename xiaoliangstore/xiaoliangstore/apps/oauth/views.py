from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework import status

from xiaoliangstore.apps.oauth.exceptions import OAuthQQAPIError
from .utils import OAuthQQ
from .models import OAuthQQUser


class OAuthQQURLView(APIView):
    """
    提供QQ登录的网址
    前端请求的接口网址  /oauth/qq/authorization/?state=xxxxxxx
    state参数是由前端传递，参数值为在QQ登录成功后，我们后端把用户引导到商城页面
    """

    def get(self, request):

        # 获取code
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        oauth_qq = OAuthQQ()
        try:
            # 凭借code 获取access_token
            access_token = oauth_qq.get_access_token(code)
            # 凭借access_token获取 openid
        except OAuthQQAPIError:
            return Response({'message': '访问QQ接口异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        openid = oauth_qq.get_openid(access_token)

        # 根据openid查询数据库OAuthQQUser  判断数据是否存在
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果数据不存在，处理openid 并返回
            access_token = OAuthQQ.generate_bind_user_access_token(openid)
            return Response({'access_token': access_token})
        else:
            # 如果数据存在，表示用户已经绑定过身份， 签发JWT token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            user = oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response({
                'username': user.username,
                'user_id': user.id,
                'token': token
            })

    class OAuthQQUserView(CreateAPIView):
        serializer_class = OAuthQQUserSerializer
