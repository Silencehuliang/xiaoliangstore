from rest_framework import serializers
from django_redis import get_redis_connection
from redis.exceptions import RedisError


class ImageCodeCheckSerializer(serializers.Serializer):
    """
    图片验证码校验序列化器
    GenericAPIView  ->  get_seriliazer()  context
    """
    # 发送的格式是uuid，而且是类似 5ce0e9a5-5ffa-654b-cee0-1238041fb31a 格式的，
    # 定义UUIDField如果不传递选项，默认就是hex_verbose，也就是符合我们指定的格式的
    image_code_id = serializers.UUIDField()
    # 4位随机字符串
    text = serializers.CharField(min_length=4, max_length=4)

    def validate(self, attrs):
        """校验图片验证码是否正确"""
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 查询redis数据库，获取真实的验证码
        redis_conn = get_redis_connection('verify_codes')
        # 从redis中获取正确的图形验证码对应的字符串
        real_image_code = redis_conn.get('img_%s' % image_code_id)
        # 删除redis中的图片验证码
        redis_conn.delete('img_%s' % image_code_id)
        if real_image_code is None:
            # 过期或者前端胡编乱造的image_code_id
            raise serializers.ValidationError('无效的图片验证码')
        # 对比从redis拿到的是 bytes类型，需要转为str类型才能比对
        real_image_code = real_image_code.decode()
        # 不区分大小写
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')
        # redis中发送短信验证码的标志 send_flag_<mobile>  : 1, 由redis维护60s的有效期
        # 手机号是关键字参数，会被添加到视图对象的 kwargs字典属性中
        mobile = self.context['view'].kwargs['mobile']
        # 这个地方目前没有对应的保存逻辑
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信次数过于频繁')
        # 校验通过返回原始数据
        return attrs
