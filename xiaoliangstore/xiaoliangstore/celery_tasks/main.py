from celery import Celery
import os

# 为celery使用django配置文件进行设置
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'xiaoliangstore.settings.dev'
# 创建出Celery对象，指定名称，并指定broker
celery_app = Celery('store', broker="redis://127.0.0.1:6379/15")
# 自动注册celery任务
# 需要指定 所有任务模块所在的包(一个也要用列表)
celery_app.autodiscover_tasks(['celery_tasks.sms'])
