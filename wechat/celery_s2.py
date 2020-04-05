#!/usr/bin/env python
# -*- coding:utf-8 -*-
from celery_s1 import x1

# 立即告知celery去执行xxxxxx任务，并传入两个参数
result = x1.delay(1, 4)
print(result.id)
