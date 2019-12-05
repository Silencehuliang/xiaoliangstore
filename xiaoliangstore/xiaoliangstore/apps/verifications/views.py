import random

from django.template.base import logger
from django_redis import get_redis_connection
from django.http.response import HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from xiaoliangstore.libs.captcha.captcha import captcha
from .serializer import ImageCodeCheckSerializer
from . import constants
from xiaoliangstore.libs.yuntongxun.sms import CCP


class ImageCodeView(APIView):
    """
    图片验证码
    """

    # 请求时需要添加图片id
    def get(self, request, image_code_id):
        # 生成验证码图片 ,获取随机文本和对应图片
        text, image = captcha.generate_captcha()
        # 获取redis的连接对象 , 需要在配置文件中配置名为verify_codes的redis缓存
        redis_conn = get_redis_connection("verify_codes")
        # 存入redis数据库，便于后面的业务进行校验，并指定过期时间自动删除
        redis_conn.setex("img_%s" % image_code_id, 300, text)
        # 返回http响应 注意指定内容类型为image/jpg 表示图片
        # 虽然我们使用的是APIView，但也可以返回 django中的 HttpResponse  drf 框架会做判断
        return HttpResponse(image, content_type="image/jpg")


class SMSCodeView(GenericAPIView):
    """
    短信验证码
    传入参数：mobile,     image_code_id, text
    """
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 校验参数  由序列化器完成
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 保存短信验证码  保存发送记录
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        redis_conn.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 发送短信
        try:
            ccp = CCP()
            expires = constants.SMS_CODE_REDIS_EXPIRES // 60
            result = ccp.send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        except Exception as e:
            logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
            return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if result == 0:
                logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
                return Response({'message': 'OK'})
            else:
                logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
                return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
