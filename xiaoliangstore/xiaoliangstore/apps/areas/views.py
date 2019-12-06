from rest_framework import serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area


class AreasViewSet(ReadOnlyModelViewSet, CacheResponseMixin):
    """
    list:
    返回所有省份的信息
    retrieve:
    返回特定省或市的下属行政规划区域
    """

    # queryset = Area.objects.all()
    def get_queryset(self):
        if self.action == 'list':  # 如果是list请求，返回的是父级区域为空的区域
            return Area.objects.filter(parent=None)
        else:  # 如果是retrieve请求，返回的是所有，由视图集来控制传入的主键，过滤出特定区域
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':  # 如果是list请求，返回的AreaSerialier(没有sub)
            return serializers.AreaSerialier
        else:  # 如果是retrieve请求，返回的SubAreaSerializer(有sub)
            return serializers.SubAreaSerializer
