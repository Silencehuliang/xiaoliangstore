from django.db import models


class BaseModel(models.Model):
    """为模型类补充字段"""
    # auto_now_add 创建模型的时候自动添加当前时间作为字段的值
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # auto_now 更新模型的时候自动添加当前时间作为字段的值
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表
