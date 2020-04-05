#进行启动celery
# 启动celery
from .celery import app as celery_app

__all__ = ('celery_app',)
