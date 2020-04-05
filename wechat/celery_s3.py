# 获取任务返回值
from celery.result import AsyncResult
from celery_s1 import app

async = AsyncResult(id="f0b41e83-99cf-469f-9eff-74c8dd600002", app=app)

if async.successful():
    result = async.get()
    print(result)
    # result.forget() # 将结果删除
elif async.failed():
    print('执行失败')
elif async.status == 'PENDING':
    print('任务等待中被执行')
elif async.status == 'RETRY':
    print('任务异常后正在重试')
elif async.status == 'STARTED':
    print('任务已经开始被执行')
