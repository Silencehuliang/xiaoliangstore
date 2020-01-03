from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings

from .exceptions import OAuthQQAPIError
from .utils import OAuthQQ
from .models import OAuthQQUser


class OAuthQQURLView(APIView):
    """
    提供QQ登录的网址
    state参数是由前端传递，参数值为在QQ登录成功后，我们后端把用户引导到哪个商城页面
    """

    def get(self, request):
        # 提取state参数
        next = request.query_params.get('next', '/')
        # 如果前端未指明，我们设置用户QQ登录成功后，跳转到主页
        # 我们把QQ登录相关操作都提取到固定的地方
        # 使用面向对象的方式是处理
        # 按照QQ的说明文档，拼接用户QQ登录的链接地址
        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_qq_login_url()
        # 返回链接地址
        return Response({"oauth_url": login_url})


class OAuthQQUserView(APIView):
    """
    获取QQ用户对应的商城用户
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
