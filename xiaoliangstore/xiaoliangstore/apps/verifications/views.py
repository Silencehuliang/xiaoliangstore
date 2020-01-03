import random
from django_redis import get_redis_connection
from django.http.response import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from xiaoliangstore.apps.verifications import constants
from xiaoliangstore.apps.verifications.serializers import ImageCodeCheckSerializer
from xiaoliangstore.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import send_sms_code


class ImageCodeView(APIView):
    """
    图片验证码
    """

    # 请求时需要添加图片id
    def get(self, request, image_code_id):
        # 生成验证码图片 ,获取随机文本和对应图片
        text, image = captcha.generate_captcha()
        print(text)
        # 获取redis的连接对象 , 需要在配置文件中配置名为verify_codes的redis缓存
        redis_conn = get_redis_connection("verify_codes")
        # 存入redis数据库，便于后面的业务进行校验，并指定过期时间 自动删除
        redis_conn.setex("img_%s" % image_code_id, 300, text)
        # 返回http响应 注意指定内容类型为image/jpg 表示图片
        # 虽然我们使用的是APIView，但也可以返回django中的HttpResponse，drf框架会做判断
        return HttpResponse(image, content_type="image/jpg")


class SMSCodeView(GenericAPIView):
    """
    短信验证码
    传入参数：
    mobile,image_code_id,text
    """
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 校验参数  由序列化器完成
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        print(sms_code)
        # 保存短信验证码  保存发送记录
        redis_conn = get_redis_connection('verify_codes')
        # 使用redis的pipeline管道一次执行多个命令
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 让管道执行命令
        pl.execute()
        # 使用celery发送短信验证码
        expires = constants.SMS_CODE_REDIS_EXPIRES
        send_sms_code.delay(mobile, sms_code, expires, constants.SMS_CODE_TEMP_ID)
