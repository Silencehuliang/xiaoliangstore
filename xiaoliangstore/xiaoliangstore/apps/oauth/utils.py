import requests
import json
import logging
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from xiaoliangstore.settings import dev
from xiaoliangstore.apps.oauth.exceptions import OAuthQQAPIError
from . import constants


class OAuthQQ(object):
    """
    用户QQ登陆的工具类，
    提供了QQ登录可能使用的方法
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id if client_id else dev.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri if redirect_uri else dev.QQ_REDIRECT_URI
        # self.state = state if state else settings.QQ_STATE
        self.state = state or dev.QQ_STATE
        self.client_secret = client_secret if client_secret else dev.QQ_CLIENT_SECRET

    def get_login_url(self):
        url = 'https://graph.qq.com/oauth2.0/authorize?'
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }

        url += requests.get(url, params).content.decode()
        return url

    def get_access_token(self, code):
        url = 'https://graph.qq.com/oauth2.0/token?'
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        url += requests.get(url, params).content.decode()
        try:
            # 发送请求
            resp_data = requests.get(url).content.decode()
            # 读取响应体数据
            # 解析 access_token
            resp_dict = json.load(resp_data)
        except Exception as e:
            logging.error('获取access_token异常：%s' % e)
            raise OAuthQQAPIError
        else:
            access_token = resp_dict.get('access_token')
            return access_token[0]

    def get_openid(self, access_token):
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        try:
            # 发送请求
            resp_data = requests.get(url).content.decode()
            # callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            # 解析
            resp_data = resp_data[10:-4]
            resp_dict = json.loads(resp_data)
        except Exception as e:
            logging.error('获取openid异常：%s' % e)
            raise OAuthQQAPIError
        else:
            openid = resp_dict.get('openid')

    @staticmethod
    def generate_bind_user_access_token(openid):
        serializer = TJWSSerializer(dev.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        token = serializer.dumps({'openid': openid})
        return token.decode()

    @staticmethod
    def check_bind_user_access_token(access_token):
        serializer = TJWSSerializer(dev.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return data['openid']
