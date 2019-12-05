from .models import Area
from rest_framework import serializers


class AreaSerialier(serializers.ModelSerializer):
    """行政区域信息序列化器"""

    class Meta:
        model = Area
        fields = ('id', 'name')


class SubAreaSerializer(serializers.ModelSerializer):
    """
    子级行政区划信息
    """
    # sub怎么来的? 我们在定义外键关联的时候指定了 related_name选项为sub代替了默认的area_set
    # 如果不定义，则返回的是主键列表
    subs = AreaSerialier(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')
